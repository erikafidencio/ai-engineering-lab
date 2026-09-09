#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from bug_investigator.config import AppConfig, project_root
from bug_investigator.rag.indexer import index_documents
from bug_investigator.rag.query import diagnose, search
from bug_investigator.rag.store import VectorStore

console = Console()


def _load_env() -> AppConfig:
    root = project_root()
    for candidate in [root / ".env", root / ".env.example"]:
        if candidate.exists():
            load_dotenv(candidate, override=False)
    return AppConfig.load()


@click.group()
def cli() -> None:
    """AI Bug Investigator — RAG CLI (MVP Part 2)."""


@cli.command("status")
def status_cmd() -> None:
    """Show index status."""
    config = _load_env()
    store = VectorStore(config)
    manifest_path = config.data_dir / "manifest.json"
    console.print(f"[bold]Project root:[/bold] {config.project_root}")
    console.print(f"[bold]Chroma path:[/bold] {config.data_dir / 'chroma'}")
    console.print(f"[bold]Chunks indexed:[/bold] {store.count()}")
    if manifest_path.exists():
        console.print(f"[bold]Manifest:[/bold] {manifest_path}")
    else:
        console.print("[yellow]Manifest not found — run `index` first.[/yellow]")


@cli.command("index")
@click.option("--no-reset", is_flag=True, help="Append without resetting the collection")
def index_cmd(no_reset: bool) -> None:
    """Index synthetic dataset into ChromaDB."""
    config = _load_env()
    console.print("[bold]Indexing synthetic dataset...[/bold]")
    result = index_documents(config, reset=not no_reset)
    if result.get("chunks", 0) == 0:
        console.print(f"[red]{result.get('message', 'Indexing failed')}[/red]")
        raise SystemExit(1)
    console.print(
        f"[green]Done:[/green] {result['documents']} docs → {result['chunks']} chunks "
        f"(collection size: {result['collection_size']})"
    )
    console.print(f"[dim]Manifest:[/dim] {result['manifest']}")


@cli.command("search")
@click.argument("query")
@click.option("--top-k", default=5, show_default=True)
@click.option("--source", default=None, help="Filter by metadata source (incident, runbook, ...)")
def search_cmd(query: str, top_k: int, source: str | None) -> None:
    """Semantic search over the index."""
    config = _load_env()
    hits = search(config, query, top_k=top_k, source_filter=source)
    if not hits:
        console.print("[yellow]No hits. Run `index` first.[/yellow]")
        raise SystemExit(1)

    table = Table(title=f"Search: {query}")
    table.add_column("Score", justify="right")
    table.add_column("Source")
    table.add_column("Title")
    for hit in hits:
        meta = hit["metadata"]
        table.add_row(
            str(hit["score"]),
            str(meta.get("source", "")),
            str(meta.get("title", ""))[:80],
        )
    console.print(table)


@cli.command("diagnose")
@click.argument("query")
@click.option("--json-out", is_flag=True, help="Print full JSON result")
def diagnose_cmd(query: str, json_out: bool) -> None:
    """Classify symptom and synthesize investigation guidance."""
    config = _load_env()
    result = diagnose(config, query)
    if json_out:
        console.print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    console.print(f"[bold]Query:[/bold] {result['query']}")
    console.print(f"[bold]Symptom:[/bold] {result.get('symptom') or 'unclassified'}")
    console.print(f"[bold]Escalate:[/bold] {result.get('escalate') or 'TBD'}")
    console.print("")
    console.print(result["diagnosis"])
    if result.get("next_steps"):
        console.print("")
        console.print("[bold]Next steps[/bold]")
        for index, step in enumerate(result["next_steps"], 1):
            console.print(f"{index}. {step}")


if __name__ == "__main__":
    cli()
