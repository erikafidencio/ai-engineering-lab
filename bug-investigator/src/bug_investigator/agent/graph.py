from __future__ import annotations

from langgraph.graph import END, StateGraph

from bug_investigator.agent.nodes.fetch_context import fetch_context
from bug_investigator.agent.nodes.parse_input import parse_input
from bug_investigator.agent.nodes.synthesize import synthesize
from bug_investigator.agent.nodes.write_output import write_output
from bug_investigator.agent.state import AgentState


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("parse_input", parse_input)
    graph.add_node("fetch_context", fetch_context)
    graph.add_node("synthesize", synthesize)
    graph.add_node("write_output", write_output)

    graph.set_entry_point("parse_input")
    graph.add_edge("parse_input", "fetch_context")
    graph.add_edge("fetch_context", "synthesize")
    graph.add_edge("synthesize", "write_output")
    graph.add_edge("write_output", END)

    return graph.compile()


def run_investigation(raw_input: str) -> AgentState:
    app = build_graph()
    return app.invoke({"raw_input": raw_input, "warnings": []})
