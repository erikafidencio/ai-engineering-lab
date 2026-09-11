from __future__ import annotations

import json
from pathlib import Path

from bug_investigator.agent.state import AgentState


def write_output(state: AgentState) -> dict:
    report = state.get("report")
    if not report:
        return {}

    output_dir = Path(state.get("output_dir", "."))
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "agent_report.json"
    md_path = output_dir / "agent_report.md"

    json_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md_path.write_text(report.to_markdown(), encoding="utf-8")

    return {
        "metadata": {
            **(report.metadata or {}),
            "json_path": str(json_path),
            "md_path": str(md_path),
        }
    }
