from __future__ import annotations

from typing import Any

from bug_investigator.config import AppConfig
from bug_investigator.rag.chunker import chunk_documents
from bug_investigator.rag.collectors import COLLECTORS
from bug_investigator.rag.collectors.base import merge_documents
from bug_investigator.rag.embedder import embed_texts
from bug_investigator.rag.store import VectorStore


def collect_documents(
    config: AppConfig,
    sources: list[str] | None = None,
) -> tuple[list, dict[str, int]]:
    selected = sources or list(COLLECTORS.keys())
    all_docs = []
    counts: dict[str, int] = {}
    for name in selected:
        collector_cls = COLLECTORS.get(name)
        if not collector_cls:
            continue
        collector = collector_cls(config)
        docs = collector.collect()
        counts[name] = len(docs)
        all_docs = merge_documents(all_docs, docs)
    return all_docs, counts


def index_documents(
    config: AppConfig,
    sources: list[str] | None = None,
    reset: bool = True,
) -> dict[str, Any]:
    documents, source_counts = collect_documents(config, sources)
    if not documents:
        return {
            "documents": 0,
            "chunks": 0,
            "source_counts": source_counts,
            "message": "No documents collected. Check data/synthetic/ paths.",
        }

    chunk_size = int(config.get("indexing", "chunk_size", default=800))
    overlap = int(config.get("indexing", "chunk_overlap", default=120))
    model_name = config.get("indexing", "embedding_model", default="all-MiniLM-L6-v2")

    chunks = chunk_documents(documents, chunk_size, overlap)
    ids = [chunk[0] for chunk in chunks]
    texts = [chunk[1] for chunk in chunks]
    metas = [chunk[2] for chunk in chunks]

    embeddings = embed_texts(model_name, texts)

    store = VectorStore(config)
    if reset:
        store.reset()
    store.upsert(ids, texts, embeddings, metas)
    manifest_path = store.save_manifest(
        {
            "documents": len(documents),
            "source_counts": source_counts,
            "embedding_model": model_name,
        }
    )

    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "source_counts": source_counts,
        "manifest": str(manifest_path),
        "collection_size": store.count(),
    }
