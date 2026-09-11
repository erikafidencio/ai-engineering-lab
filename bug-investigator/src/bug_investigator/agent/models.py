from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ReportSection:
    title: str
    content: str
    items: list[str] = field(default_factory=list)


@dataclass
class AgentReport:
    input_type: str
    input_value: str
    issue_key: str | None
    generated_at: str
    sections: dict[str, ReportSection]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def section_titles() -> list[str]:
        return [
            "business_summary",
            "ticket_state",
            "historical_patterns",
            "live_evidence",
            "probable_diagnosis",
            "next_steps",
            "escalate_to",
        ]

    @staticmethod
    def section_labels() -> dict[str, str]:
        return {
            "business_summary": "1) Incident summary (business)",
            "ticket_state": "2) Ticket state",
            "historical_patterns": "3) Historical patterns (RAG)",
            "live_evidence": "4) Live evidence (logs / ticket)",
            "probable_diagnosis": "5) Probable diagnosis",
            "next_steps": "6) Next steps (ordered)",
            "escalate_to": "7) Escalate to",
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_type": self.input_type,
            "input_value": self.input_value,
            "issue_key": self.issue_key,
            "generated_at": self.generated_at,
            "warnings": self.warnings,
            "metadata": self.metadata,
            "sections": {
                key: {
                    "title": section.title,
                    "content": section.content,
                    "items": section.items,
                }
                for key, section in self.sections.items()
            },
        }

    def to_markdown(self) -> str:
        lines = [
            f"# Investigation report — {self.input_value}",
            "",
            f"**Generated at:** {self.generated_at}",
            f"**Type:** {self.input_type}",
        ]
        if self.issue_key:
            lines.append(f"**Ticket:** {self.issue_key}")
        if self.warnings:
            lines.append("")
            lines.append("## Warnings")
            for warning in self.warnings:
                lines.append(f"- {warning}")
        lines.append("")
        for key in self.section_titles():
            section = self.sections.get(key)
            if not section:
                continue
            lines.append(f"## {section.title}")
            lines.append("")
            if section.content:
                lines.append(section.content)
                lines.append("")
            if section.items:
                for index, item in enumerate(section.items, 1):
                    lines.append(f"{index}. {item}")
                lines.append("")
        return "\n".join(lines).rstrip() + "\n"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
