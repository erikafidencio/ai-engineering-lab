from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bug_investigator.config import AppConfig
from bug_investigator.rag.collectors.synthetic import SyntheticCollector
from bug_investigator.rag.indexer import index_documents
from bug_investigator.rag.query import classify_symptom, diagnose, search


@pytest.fixture(scope="module")
def config() -> AppConfig:
    return AppConfig.load(ROOT / "config.yaml")


def test_synthetic_collector_loads_all_docs(config: AppConfig) -> None:
    docs = SyntheticCollector(config).collect()
    assert len(docs) >= 8
    sources = {doc.source for doc in docs}
    assert "incident" in sources
    assert "runbook" in sources
    assert "observability" in sources


def test_classify_orders_missing(config: AppConfig) -> None:
    symptom, escalate = classify_symptom(config, "merchant dashboard empty ORD-Ingest trace")
    assert symptom == "orders_missing"
    assert escalate is not None


def test_index_and_search_incident(config: AppConfig) -> None:
    result = index_documents(config, reset=True)
    assert result["chunks"] > 0

    hits = search(config, "ORD-Ingest-a1b2c3d4e5f6789012345678abcdef01", top_k=3)
    assert hits
    issue_keys = {hit["metadata"].get("issue_key") for hit in hits}
    assert "INC-1001" in issue_keys


def test_diagnose_duplicate_charge(config: AppConfig) -> None:
    index_documents(config, reset=False)
    result = diagnose(config, "double charge PAY-409 idempotency retry")
    assert result["symptom"] == "duplicate_charge"
    assert result["hits"]
