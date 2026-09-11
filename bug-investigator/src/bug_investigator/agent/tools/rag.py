from __future__ import annotations

from typing import Any

from bug_investigator.config import AppConfig
from bug_investigator.rag.query import diagnose


def rag_search(query: str, config: AppConfig, top_k: int = 8) -> dict[str, Any]:
    result: dict[str, Any] = {
        "available": False,
        "query": query,
        "symptom": None,
        "escalate": None,
        "diagnosis": "",
        "next_steps": [],
        "hits": [],
        "warning": None,
    }

    try:
        diag = diagnose(config, query, top_k=top_k)
        result.update(
            {
                "available": bool(diag.get("hits")),
                "symptom": diag.get("symptom"),
                "escalate": diag.get("escalate"),
                "diagnosis": diag.get("diagnosis", ""),
                "next_steps": diag.get("next_steps", []),
                "hits": [
                    {
                        "title": hit["metadata"].get("title"),
                        "source": hit["metadata"].get("source"),
                        "issue_key": hit["metadata"].get("issue_key"),
                        "score": hit.get("score"),
                        "snippet": hit.get("content", "")[:300],
                    }
                    for hit in diag.get("hits", [])[:8]
                ],
            }
        )
        if not diag.get("hits"):
            result["warning"] = "RAG index empty. Run `./scripts/index.sh` first."
    except Exception as exc:
        result["warning"] = f"RAG unavailable: {exc}"

    return result
