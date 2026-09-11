from __future__ import annotations

from bug_investigator.agent.models import AgentReport, ReportSection, utc_now_iso
from bug_investigator.agent.state import AgentState


def synthesize(state: AgentState) -> dict:
    labels = AgentReport.section_labels()
    warnings = list(state.get("warnings") or [])
    input_type = state.get("input_type", "symptom")
    input_value = state.get("raw_input", "")
    issue_key = state.get("issue_key")
    jira = state.get("jira_context") or {}
    logs = state.get("logs_context") or {}
    rag = state.get("rag_result") or {}

    sections: dict[str, ReportSection] = {}

    if jira.get("available") and jira.get("issue"):
        issue = jira["issue"]
        sections["business_summary"] = ReportSection(
            title=labels["business_summary"],
            content=(
                f"**{issue.get('key')}** — {issue.get('summary', 'no title')}\n\n"
                f"Priority: {issue.get('priority', '—')}\n"
                f"URL: {issue.get('url', '—')}"
            ),
        )
    elif input_type == "issue" and issue_key:
        sections["business_summary"] = ReportSection(
            title=labels["business_summary"],
            content=f"Ticket **{issue_key}** — mock Jira data not found in data/synthetic/incidents/.",
        )
    else:
        sections["business_summary"] = ReportSection(
            title=labels["business_summary"],
            content=f"Reported symptom: {input_value}",
        )

    if jira.get("available") and jira.get("issue"):
        issue = jira["issue"]
        sections["ticket_state"] = ReportSection(
            title=labels["ticket_state"],
            content=(
                f"**Status:** {issue.get('status', '—')}\n"
                f"**Priority:** {issue.get('priority', '—')}\n"
                f"**Labels:** {', '.join(issue.get('labels', [])) or '—'}\n"
                f"**Source:** {jira.get('source', 'mock_jira')}"
            ),
        )
    else:
        sections["ticket_state"] = ReportSection(
            title=labels["ticket_state"],
            content="No ticket loaded (symptom-only investigation).",
        )

    if rag.get("available") or rag.get("symptom"):
        hit_lines = []
        for hit in rag.get("hits", [])[:5]:
            issue_ref = f" ({hit['issue_key']})" if hit.get("issue_key") else ""
            hit_lines.append(
                f"- [{hit.get('source')}] {hit.get('title')}{issue_ref} (score {hit.get('score')})"
            )
        sections["historical_patterns"] = ReportSection(
            title=labels["historical_patterns"],
            content=(
                f"**Classified symptom:** {rag.get('symptom') or 'unclassified'}\n\n"
                + (rag.get("diagnosis") or "")
                + ("\n\n**Hits:**\n" + "\n".join(hit_lines) if hit_lines else "")
            ),
        )
    else:
        sections["historical_patterns"] = ReportSection(
            title=labels["historical_patterns"],
            content="RAG index unavailable or empty. Run `./scripts/index.sh`.",
        )

    live_lines: list[str] = []
    if jira.get("source"):
        live_lines.append(f"- Ticket: {jira['source']}")
    if logs.get("available"):
        live_lines.append(
            f"- Observability: {len(logs.get('hits', []))} log bundle(s), "
            f"traces={', '.join(logs.get('trace_ids', [])[:2]) or '—'}"
        )
        if logs.get("summary"):
            live_lines.append("")
            live_lines.append(logs["summary"])
    elif logs.get("trace_ids"):
        live_lines.append(
            f"- Observability: no mock logs matched (traces: {', '.join(logs['trace_ids'][:2])})"
        )
    else:
        live_lines.append("- Observability: no trace IDs detected in context")
    sections["live_evidence"] = ReportSection(
        title=labels["live_evidence"],
        content="\n".join(live_lines),
    )

    diagnosis_parts: list[str] = []
    if logs.get("summary") and logs.get("available"):
        diagnosis_parts.append(logs["summary"][:2500])
    elif rag.get("diagnosis"):
        diagnosis_parts.append(rag["diagnosis"][:1500])
    sections["probable_diagnosis"] = ReportSection(
        title=labels["probable_diagnosis"],
        content="\n\n".join(diagnosis_parts) if diagnosis_parts else "Insufficient data for automatic diagnosis.",
    )

    steps: list[str] = []
    for step in rag.get("next_steps", []):
        if step and step not in steps:
            steps.append(step)
    if not steps:
        steps = [
            "Run `./scripts/index.sh` if RAG hits are empty",
            "Correlate trace IDs across mock logs and ticket description",
            "Follow the matching runbook in data/synthetic/runbooks/",
        ]
    sections["next_steps"] = ReportSection(
        title=labels["next_steps"],
        content="",
        items=steps[:7],
    )

    escalate = rag.get("escalate")
    if logs.get("available") and logs.get("hits"):
        services = logs["hits"][0].get("services", [])
        if services:
            escalate = escalate or services[0]
    sections["escalate_to"] = ReportSection(
        title=labels["escalate_to"],
        content=escalate or "Platform on-call (define after triage)",
    )

    report = AgentReport(
        input_type=input_type,
        input_value=input_value,
        issue_key=issue_key,
        generated_at=utc_now_iso(),
        sections=sections,
        warnings=warnings,
        metadata={
            "output_slug": state.get("output_slug"),
            "jira_source": jira.get("source"),
            "rag_symptom": rag.get("symptom"),
            "log_hits": len(logs.get("hits", [])),
            "rag_hits": len(rag.get("hits", [])),
        },
    )

    return {"report": report, "warnings": warnings}
