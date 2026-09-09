from __future__ import annotations

import json
from pathlib import Path

from bug_investigator.config import AppConfig
from bug_investigator.models import Document


class SyntheticCollector:
    name = "synthetic"

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.base = config.resolve_path("data/synthetic")

    def collect(self) -> list[Document]:
        docs: list[Document] = []
        docs.extend(self._collect_incidents())
        docs.extend(self._collect_runbooks())
        docs.extend(self._collect_logs())
        docs.extend(self._collect_cheatsheet())
        return docs

    def _collect_incidents(self) -> list[Document]:
        incidents_dir = self.config.resolve_path(
            self.config.get("synthetic_data", "incidents_dir", default="data/synthetic/incidents")
        )
        docs: list[Document] = []
        for path in sorted(incidents_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            key = payload.get("key", path.stem)
            comments = "\n".join(
                f"[{c.get('author', 'unknown')}]: {c.get('body', '')}"
                for c in payload.get("comments", [])
            )
            content = "\n\n".join(
                part
                for part in [
                    f"Summary: {payload.get('summary', '')}",
                    f"Status: {payload.get('status', '')}",
                    f"Priority: {payload.get('priority', '')}",
                    f"Labels: {', '.join(payload.get('labels', []))}",
                    f"Description:\n{payload.get('description', '')}",
                    f"Comments:\n{comments}" if comments else "",
                ]
                if part
            )
            docs.append(
                Document(
                    id=f"incident:{key}",
                    source="incident",
                    title=f"{key} — {payload.get('summary', '')}",
                    content=content,
                    metadata={
                        "issue_key": key,
                        "url": payload.get("url"),
                        "status": payload.get("status"),
                        "type": "ticket",
                    },
                )
            )
        return docs

    def _collect_runbooks(self) -> list[Document]:
        runbooks_dir = self.config.resolve_path(
            self.config.get("synthetic_data", "runbooks_dir", default="data/synthetic/runbooks")
        )
        docs: list[Document] = []
        for path in sorted(runbooks_dir.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            title = _extract_title(content) or path.stem
            docs.append(
                Document(
                    id=f"runbook:{path.stem}",
                    source="runbook",
                    title=title,
                    content=content,
                    metadata={"path": str(path.relative_to(self.config.project_root)), "type": "runbook"},
                )
            )
        return docs

    def _collect_logs(self) -> list[Document]:
        logs_dir = self.config.resolve_path(
            self.config.get("synthetic_data", "logs_dir", default="data/synthetic/logs")
        )
        docs: list[Document] = []
        for path in sorted(logs_dir.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            incident_key = payload.get("incident_key", path.stem)
            lines = [
                f"Incident: {incident_key}",
                f"Trace: {payload.get('trace_id', '')}",
                f"Environment: {payload.get('environment', '')}",
                f"Region: {payload.get('region', '')}",
                f"Services: {', '.join(payload.get('services', []))}",
                "",
                "Log entries:",
            ]
            for entry in payload.get("entries", []):
                lines.append(
                    f"- [{entry.get('timestamp')}] {entry.get('level')} "
                    f"{entry.get('entity.name', '')}: {entry.get('message')}"
                )
            docs.append(
                Document(
                    id=f"logs:{incident_key}",
                    source="observability",
                    title=f"Observability logs — {incident_key}",
                    content="\n".join(lines),
                    metadata={
                        "issue_key": incident_key,
                        "trace_id": payload.get("trace_id"),
                        "type": "logs",
                    },
                )
            )
        return docs

    def _collect_cheatsheet(self) -> list[Document]:
        cheatsheet = self.base / "cheatsheet.md"
        if not cheatsheet.exists():
            return []
        content = cheatsheet.read_text(encoding="utf-8")
        return [
            Document(
                id="cheatsheet:main",
                source="cheatsheet",
                title="ShopFlow incident cheatsheet",
                content=content,
                metadata={"path": "data/synthetic/cheatsheet.md", "type": "cheatsheet"},
            )
        ]


def _extract_title(content: str) -> str | None:
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None
