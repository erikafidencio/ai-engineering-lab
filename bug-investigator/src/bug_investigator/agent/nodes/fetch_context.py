from __future__ import annotations

from bug_investigator.agent.state import AgentState
from bug_investigator.agent.tools.mock_jira import jira_get_issue
from bug_investigator.agent.tools.mock_observability import observability_search
from bug_investigator.agent.tools.rag import rag_search
from bug_investigator.config import AppConfig


def fetch_context(state: AgentState) -> dict:
    config = AppConfig.load()
    warnings = list(state.get("warnings") or [])
    input_type = state.get("input_type", "symptom")
    issue_key = state.get("issue_key")
    symptom_query = state.get("symptom_query", "")

    jira_context = None
    logs_context = None
    rag_query = symptom_query or state.get("raw_input", "")

    if input_type == "issue" and issue_key:
        jira_context = jira_get_issue(issue_key, config)
        if jira_context.get("warning"):
            warnings.append(jira_context["warning"])
        if jira_context.get("text"):
            rag_query = f"{issue_key} {jira_context['text'][:2000]}"
        logs_context = observability_search(
            jira_context.get("text", ""),
            config,
            issue_key=issue_key,
        )
    else:
        logs_context = observability_search(rag_query, config)

    if logs_context and logs_context.get("warning"):
        warnings.append(logs_context["warning"])

    rag_result = rag_search(rag_query, config)
    if rag_result.get("warning"):
        warnings.append(rag_result["warning"])

    return {
        "jira_context": jira_context,
        "logs_context": logs_context,
        "rag_result": rag_result,
        "warnings": warnings,
    }
