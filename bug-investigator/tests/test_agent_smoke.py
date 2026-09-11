from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bug_investigator.agent.graph import run_investigation
from bug_investigator.agent.models import AgentReport
from bug_investigator.config import AppConfig
from bug_investigator.rag.indexer import index_documents


@pytest.fixture(scope="module")
def indexed_config() -> AppConfig:
    config = AppConfig.load(ROOT / "config.yaml")
    index_documents(config, reset=True)
    return config


def test_investigate_ticket(indexed_config: AppConfig) -> None:
    result = run_investigation("INC-1001")
    report = result.get("report")
    assert report is not None
    assert report.issue_key == "INC-1001"
    assert "business_summary" in report.sections
    assert "live_evidence" in report.sections
    assert report.metadata.get("rag_symptom") == "orders_missing"

    output_dir = Path(result["output_dir"])
    json_path = output_dir / "agent_report.json"
    md_path = output_dir / "agent_report.md"
    assert json_path.exists()
    assert md_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["issue_key"] == "INC-1001"
    assert len(payload["sections"]) == len(AgentReport.section_titles())


def test_investigate_symptom(indexed_config: AppConfig) -> None:
    result = run_investigation("double charge PAY-409 idempotency")
    report = result.get("report")
    assert report is not None
    assert report.input_type == "symptom"
    assert report.metadata.get("rag_symptom") == "duplicate_charge"
