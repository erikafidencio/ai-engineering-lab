from __future__ import annotations

from typing import Any, Optional, TypedDict

from bug_investigator.agent.models import AgentReport


class AgentState(TypedDict, total=False):
    raw_input: str
    input_type: str
    issue_key: Optional[str]
    symptom_query: str
    output_slug: str
    output_dir: str
    warnings: list[str]
    jira_context: Optional[dict[str, Any]]
    logs_context: Optional[dict[str, Any]]
    rag_result: Optional[dict[str, Any]]
    report: Optional[AgentReport]
    metadata: dict[str, Any]
