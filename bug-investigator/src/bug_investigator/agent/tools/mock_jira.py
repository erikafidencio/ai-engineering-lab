from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from bug_investigator.config import AppConfig

ISSUE_KEY_RE = re.compile(r"^INC-\d+$", re.I)


def jira_get_issue(issue_key: str, config: AppConfig) -> dict[str, Any]:
    key = issue_key.upper()
    result: dict[str, Any] = {
        "issue_key": key,
        "available": False,
        "source": None,
        "issue": None,
        "text": "",
        "warning": None,
    }

    incidents_dir = config.resolve_path(
        config.get("synthetic_data", "incidents_dir", default="data/synthetic/incidents")
    )
    path = incidents_dir / f"{key}.json"
    if not path.exists():
        result["warning"] = f"Mock ticket not found: {path}"
        return result

    payload = json.loads(path.read_text(encoding="utf-8"))
    comments = "\n".join(
        f"[{comment.get('author', 'unknown')}]: {comment.get('body', '')}"
        for comment in payload.get("comments", [])
    )
    text = "\n\n".join(
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

    result.update(
        {
            "available": True,
            "source": "mock_jira",
            "issue": {
                "key": key,
                "summary": payload.get("summary", ""),
                "status": payload.get("status"),
                "priority": payload.get("priority"),
                "labels": payload.get("labels", []),
                "url": payload.get("url"),
            },
            "text": text,
        }
    )
    return result
