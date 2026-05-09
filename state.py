from typing import TypedDict


class CodeReviewState(TypedDict):
    code: str
    language: str
    complexity_score: int
    has_user_input: bool
    checks_needed: list[str]
    bug_findings: list[dict]
    style_findings: list[dict]
    security_findings: list[dict]
    synthesized_findings: list[dict]
    fix_suggestions: list[dict]
    human_feedback: str
    final_report: str
