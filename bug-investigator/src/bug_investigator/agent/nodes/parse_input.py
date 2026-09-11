from __future__ import annotations

import hashlib
import re

from bug_investigator.agent.state import AgentState
from bug_investigator.agent.tools.mock_jira import ISSUE_KEY_RE
from bug_investigator.config import project_root


def parse_input(state: AgentState) -> dict:
    raw = (state.get("raw_input") or "").strip().strip('"').strip("'")
    warnings = list(state.get("warnings") or [])

    if ISSUE_KEY_RE.match(raw):
        input_type = "issue"
        issue_key = raw.upper()
        symptom_query = ""
        output_slug = issue_key
    else:
        input_type = "symptom"
        issue_key = None
        symptom_query = raw
        slug = re.sub(r"[^\w\-]+", "-", raw.lower())[:40].strip("-")
        if not slug:
            slug = hashlib.md5(raw.encode()).hexdigest()[:8]
        output_slug = f"symptom-{slug}"

    root = project_root()
    output_dir = str(root / "output" / output_slug)

    return {
        "input_type": input_type,
        "issue_key": issue_key,
        "symptom_query": symptom_query,
        "output_slug": output_slug,
        "output_dir": output_dir,
        "warnings": warnings,
    }
