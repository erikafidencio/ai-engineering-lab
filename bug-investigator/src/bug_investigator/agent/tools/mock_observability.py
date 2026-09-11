from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from bug_investigator.config import AppConfig

_TRACE_RE = re.compile(
    r"(ORD-Ingest-[0-9a-fA-F]+|PAY-Trace-[0-9a-zA-Z]+|INV-Sync-[0-9TZ:\-.]+)"
)


def extract_trace_ids(text: str) -> list[str]:
    return list(dict.fromkeys(_TRACE_RE.findall(text)))


def observability_search(
    text: str,
    config: AppConfig,
    issue_key: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "available": False,
        "source": None,
        "trace_ids": extract_trace_ids(text),
        "hits": [],
        "summary": "",
        "warning": None,
    }

    logs_dir = config.resolve_path(
        config.get("synthetic_data", "logs_dir", default="data/synthetic/logs")
    )
    paths: list[Path] = []
    if issue_key:
        dedicated = logs_dir / f"{issue_key.upper()}.json"
        if dedicated.exists():
            paths.append(dedicated)
    if not paths:
        paths = sorted(logs_dir.glob("*.json"))

    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        incident_key = payload.get("incident_key", path.stem)
        if issue_key and incident_key.upper() != issue_key.upper():
            continue
        trace_id = payload.get("trace_id", "")
        if issue_key or not result["trace_ids"] or trace_id in result["trace_ids"]:
            result["hits"].append(_format_log_hit(payload))
            result["available"] = True
            result["source"] = "mock_observability"

    if not result["hits"] and result["trace_ids"]:
        result["warning"] = "Trace IDs found in ticket but no matching mock log file."

    if result["hits"]:
        result["summary"] = _summarize_hits(result["hits"])

    return result


def _format_log_hit(payload: dict[str, Any]) -> dict[str, Any]:
    errors = [entry for entry in payload.get("entries", []) if entry.get("level") == "ERROR"]
    warnings = [entry for entry in payload.get("entries", []) if entry.get("level") == "WARN"]
    return {
        "incident_key": payload.get("incident_key"),
        "trace_id": payload.get("trace_id"),
        "environment": payload.get("environment"),
        "region": payload.get("region"),
        "services": payload.get("services", []),
        "error_count": len(errors),
        "warn_count": len(warnings),
        "entries": payload.get("entries", []),
    }


def _summarize_hits(hits: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for hit in hits[:2]:
        lines.append(
            f"**{hit['incident_key']}** trace `{hit['trace_id']}` "
            f"({hit['environment']}/{hit['region']}) — "
            f"{hit['error_count']} error(s), {hit['warn_count']} warning(s)"
        )
        for entry in hit["entries"]:
            if entry.get("level") in {"ERROR", "WARN"}:
                lines.append(
                    f"- [{entry.get('timestamp')}] {entry.get('entity.name')}: "
                    f"{entry.get('message')}"
                )
    return "\n".join(lines)
