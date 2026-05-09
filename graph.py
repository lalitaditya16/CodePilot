from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from nodes import (
    analyze_style,
    detect_bugs,
    generate_final_report,
    human_review,
    parse_code,
    route_checks,
    scan_security,
    suggest_fixes,
    synthesize_findings,
)
from state import CodeReviewState


def build_graph():
    workflow = StateGraph(CodeReviewState)

    workflow.add_node("parse",            parse_code)
    workflow.add_node("router",           route_checks)
    workflow.add_node("bug_detector",     detect_bugs)
    workflow.add_node("style_analyzer",   analyze_style)
    workflow.add_node("security_scanner", scan_security)
    workflow.add_node("synthesizer",      synthesize_findings)
    workflow.add_node("fix_suggester",    suggest_fixes)
    workflow.add_node("human_review",     human_review)
    workflow.add_node("final_report",     generate_final_report)

    # Entry → parse → router
    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "router")

    # Fan-out: router → 3 agents in parallel
    workflow.add_edge("router", "bug_detector")
    workflow.add_edge("router", "style_analyzer")
    workflow.add_edge("router", "security_scanner")

    # Fan-in: all 3 agents → synthesizer
    workflow.add_edge("bug_detector",     "synthesizer")
    workflow.add_edge("style_analyzer",   "synthesizer")
    workflow.add_edge("security_scanner", "synthesizer")

    # Linear tail
    workflow.add_edge("synthesizer",   "fix_suggester")
    workflow.add_edge("fix_suggester", "human_review")
    workflow.add_edge("human_review",  "final_report")
    workflow.add_edge("final_report",  END)

    return workflow.compile(checkpointer=MemorySaver())
