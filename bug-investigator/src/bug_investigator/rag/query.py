from __future__ import annotations

import os
import re
from typing import Any

import requests

from bug_investigator.config import AppConfig
from bug_investigator.rag.embedder import embed_texts
from bug_investigator.rag.store import VectorStore


def search(
    config: AppConfig,
    query: str,
    top_k: int = 8,
    source_filter: str | None = None,
) -> list[dict[str, Any]]:
    store = VectorStore(config)
    if store.count() == 0:
        return []

    model_name = config.get("indexing", "embedding_model", default="all-MiniLM-L6-v2")
    query_vec = embed_texts(model_name, [query])[0]
    results = store.query(query_vec, n_results=top_k, source_filter=source_filter)

    hits: list[dict[str, Any]] = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for doc, meta, dist in zip(docs, metas, distances):
        hits.append(
            {
                "content": doc,
                "metadata": meta,
                "score": round(1 - dist, 4),
            }
        )
    return hits


def classify_symptom(config: AppConfig, query: str) -> tuple[str | None, str | None]:
    symptoms = config.get("symptoms", default={}) or {}
    query_lower = query.lower()
    best_id = None
    best_score = 0.0
    for symptom_id, data in symptoms.items():
        score = 0.0
        for keyword in data.get("keywords", []):
            if keyword.lower() in query_lower:
                score += 1.0 + len(keyword.split()) * 0.5
        if score > best_score:
            best_score = score
            best_id = symptom_id
    if best_id and best_score > 0:
        return best_id, symptoms[best_id].get("escalate")
    return None, None


def diagnose(config: AppConfig, query: str, top_k: int = 8) -> dict[str, Any]:
    hits = search(config, query, top_k=top_k)
    symptom_id, escalate = classify_symptom(config, query)

    if not hits:
        return {
            "query": query,
            "symptom": symptom_id,
            "escalate": escalate,
            "diagnosis": "Index is empty. Run `./scripts/index.sh` first.",
            "hits": [],
            "next_steps": [
                "Run indexing: ./scripts/index.sh",
                "Verify data/synthetic/ contains incidents and runbooks",
            ],
        }

    synthesis = _synthesize_with_openai(query, hits, symptom_id, escalate)
    if not synthesis:
        synthesis = _template_diagnosis(query, hits, symptom_id, escalate)

    return {
        "query": query,
        "symptom": symptom_id,
        "escalate": escalate,
        "diagnosis": synthesis["diagnosis"],
        "next_steps": synthesis["next_steps"],
        "hits": hits,
    }


def _synthesize_with_openai(
    query: str,
    hits: list[dict[str, Any]],
    symptom_id: str | None,
    escalate: str | None,
) -> dict[str, list[str] | str] | None:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None
    context = "\n\n---\n\n".join(
        f"[{hit['metadata'].get('source')}] {hit['metadata'].get('title')}\n{hit['content'][:1200]}"
        for hit in hits[:6]
    )
    prompt = f"""You are an SRE investigating a ShopFlow e-commerce incident.
Use ONLY the retrieved context below.

Detected symptom: {symptom_id or 'unclassified'}
Escalate to: {escalate or 'TBD'}

Operator question:
{query}

Retrieved context:
{context}

Respond in English with:
1) Probable diagnosis (2-4 sentences)
2) Next steps (numbered list, max 5)
3) Evidence cited (tickets, runbooks, log patterns)
"""
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=60,
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"]
        steps = re.findall(r"^\d+[\).\]]\s+(.+)$", text, flags=re.M)
        return {"diagnosis": text, "next_steps": steps[:5] or ["Review retrieved hits"]}
    except Exception:
        return None


def _template_diagnosis(
    query: str,
    hits: list[dict[str, Any]],
    symptom_id: str | None,
    escalate: str | None,
) -> dict[str, list[str] | str]:
    lines = [
        f"**Probable symptom:** {symptom_id or 'unclassified'}",
        f"**Escalate to:** {escalate or 'Platform on-call'}",
        "",
        "**Similar historical context:**",
    ]
    for hit in hits[:5]:
        meta = hit["metadata"]
        title = meta.get("title", "untitled")
        source = meta.get("source", "")
        issue_key = meta.get("issue_key")
        suffix = f" ({issue_key})" if issue_key else ""
        lines.append(f"- [{source}] {title}{suffix} (score {hit['score']})")

    next_steps = _default_next_steps(symptom_id)
    lines.append("")
    lines.append("**Suggested next steps:**")
    for index, step in enumerate(next_steps, 1):
        lines.append(f"{index}. {step}")

    return {"diagnosis": "\n".join(lines), "next_steps": next_steps}


def _default_next_steps(symptom_id: str | None) -> list[str]:
    if symptom_id == "orders_missing":
        return [
            "Find ORD-Ingest trace in observability and check order-consumer lag",
            "Inspect DLQ for validation errors (affected=0)",
            "Confirm storeId and region in the payload",
        ]
    if symptom_id == "duplicate_charge":
        return [
            "Compare Idempotency-Key header on first attempt vs client retry",
            "Search PAY-409 in payment-service logs",
            "Collect both charge IDs for refund workflow",
        ]
    if symptom_id == "inventory_stale":
        return [
            "Compare inventory-api quantity vs edge cache value",
            "Check INV-Sync job recency and INV-lag metric",
            "Validate cache TTL against sync interval",
        ]
    return [
        "Review top RAG hits and map to incident ticket",
        "Correlate trace IDs across observability entries",
        "Follow the matching runbook escalation path",
    ]
