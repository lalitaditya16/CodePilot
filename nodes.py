import ast
import json
import os
import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.types import interrupt

from state import CodeReviewState

MODEL = "llama-3.3-70b-versatile"


def _llm():
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name=MODEL,
        temperature=0.1,
        max_tokens=2048,
    )


def _parse_json(content: str) -> list:
    content = re.sub(r"```(?:json)?\n?", "", content).strip().strip("`").strip()
    start, end = content.find("["), content.rfind("]") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass
    return []


# ── Node 1: Parse ─────────────────────────────────────────────────────────────

def parse_code(state: CodeReviewState) -> dict:
    code = state["code"]
    complexity_score = 0
    has_user_input = False
    language = "python"

    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
                complexity_score += 1
            if isinstance(node, ast.Call):
                func = node.func
                name = getattr(func, "id", "") or getattr(func, "attr", "")
                if name in ("input", "request", "form", "get", "post", "args", "json"):
                    has_user_input = True
    except SyntaxError:
        language = "unknown"

    return {
        "language": language,
        "complexity_score": complexity_score,
        "has_user_input": has_user_input,
    }


# ── Node 2: Router ────────────────────────────────────────────────────────────

def route_checks(state: CodeReviewState) -> dict:
    checks = ["bugs", "style"]
    if state.get("has_user_input") or state.get("complexity_score", 0) > 5:
        checks.append("security")
    return {"checks_needed": checks}


# ── Node 3: Bug Detector ──────────────────────────────────────────────────────

def detect_bugs(state: CodeReviewState) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a bug detection expert. Find logical bugs, runtime errors, off-by-one errors, "
         "null/None access issues, and incorrect logic. "
         "Return ONLY a valid JSON array. Each item must have: "
         "id (e.g. 'bug_1'), severity ('critical'|'high'|'medium'|'low'), "
         "line (integer or null), description (string), code_snippet (string)."),
        ("human", "Analyze this {language} code:\n```\n{code}\n```"),
    ])
    result = (prompt | _llm()).invoke({"code": state["code"], "language": state["language"]})
    return {"bug_findings": _parse_json(result.content)}


# ── Node 4: Style Analyzer ────────────────────────────────────────────────────

def analyze_style(state: CodeReviewState) -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a code quality expert. Check for high function complexity, poor naming, "
         "code duplication, and readability issues. "
         "Return ONLY a valid JSON array. Each item must have: "
         "id (e.g. 'style_1'), severity ('high'|'medium'|'low'), "
         "line (integer or null), description (string), code_snippet (string)."),
        ("human", "Analyze this {language} code:\n```\n{code}\n```"),
    ])
    result = (prompt | _llm()).invoke({"code": state["code"], "language": state["language"]})
    return {"style_findings": _parse_json(result.content)}


# ── Node 5: Security Scanner (conditional) ────────────────────────────────────

def scan_security(state: CodeReviewState) -> dict:
    if "security" not in state.get("checks_needed", []):
        return {"security_findings": []}

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a security expert. Check for SQL injection, XSS, command injection, "
         "hardcoded credentials, unvalidated input, and other OWASP Top 10 vulnerabilities. "
         "Return ONLY a valid JSON array. Each item must have: "
         "id (e.g. 'sec_1'), severity ('critical'|'high'|'medium'|'low'), "
         "line (integer or null), description (string), code_snippet (string), "
         "cwe (CWE reference string or null)."),
        ("human", "Analyze this {language} code:\n```\n{code}\n```"),
    ])
    result = (prompt | _llm()).invoke({"code": state["code"], "language": state["language"]})
    return {"security_findings": _parse_json(result.content)}


# ── Node 6: Synthesizer ───────────────────────────────────────────────────────

def synthesize_findings(state: CodeReviewState) -> dict:
    all_findings = (
        state.get("bug_findings", [])
        + state.get("style_findings", [])
        + state.get("security_findings", [])
    )

    if not all_findings:
        return {"synthesized_findings": []}

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a senior code reviewer. Given findings from multiple specialist agents: "
         "1) Remove exact duplicates, 2) Merge overlapping issues, 3) Sort by severity "
         "(critical first). Return ONLY a valid JSON array. Each item must have: "
         "id, severity ('critical'|'high'|'medium'|'low'), type ('bug'|'style'|'security'), "
         "line (integer or null), description (string), code_snippet (string)."),
        ("human", "Synthesize these findings:\n{findings}"),
    ])
    result = (prompt | _llm()).invoke({"findings": json.dumps(all_findings, indent=2)})
    synthesized = _parse_json(result.content)
    return {"synthesized_findings": synthesized if synthesized else all_findings}


# ── Node 7: Fix Suggester ─────────────────────────────────────────────────────

def suggest_fixes(state: CodeReviewState) -> dict:
    findings = state.get("synthesized_findings", [])

    if not findings:
        return {"fix_suggestions": []}

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a code fix expert. For each finding, suggest a targeted fix. "
         "Do NOT rewrite the entire function. Only show the specific lines that should change. "
         "Return ONLY a valid JSON array. Each item must have: "
         "finding_id (matches the finding id), "
         "suggested_fix (corrected code snippet only, string), "
         "explanation (why this fix works, 1-2 sentences), "
         "confidence ('high'|'medium'|'low')."),
        ("human",
         "Original {language} code:\n```\n{code}\n```\n\nFindings:\n{findings}"),
    ])
    result = (prompt | _llm()).invoke({
        "code": state["code"],
        "language": state["language"],
        "findings": json.dumps(findings, indent=2),
    })
    return {"fix_suggestions": _parse_json(result.content)}


# ── Node 8: Human Review (interrupt) ─────────────────────────────────────────

def build_review_summary(state: CodeReviewState) -> str:
    findings = state.get("synthesized_findings", [])
    suggestions = state.get("fix_suggestions", [])
    fix_map = {s["finding_id"]: s for s in suggestions if "finding_id" in s}

    lines = [
        "",
        "=" * 62,
        "  CODEPILOT REVIEW — AWAITING YOUR APPROVAL",
        "=" * 62,
    ]

    for sev in ["critical", "high", "medium", "low"]:
        tier = [f for f in findings if f.get("severity") == sev]
        if not tier:
            continue
        lines.append(f"\n  {sev.upper()}  ({len(tier)})")
        lines.append("  " + "-" * 40)
        for f in tier:
            line_ref = f" — line {f['line']}" if f.get("line") else ""
            lines.append(f"  [{f.get('type','?').upper()}]{line_ref}")
            lines.append(f"    {f.get('description', '')}")
            if f.get("code_snippet"):
                lines.append(f"    Code:  {f['code_snippet'][:90]}")
            fix = fix_map.get(f.get("id"))
            if fix:
                conf = fix.get("confidence", "?")
                lines.append(f"    Fix ({conf}):  {fix.get('suggested_fix', '')[:90]}")
                lines.append(f"    Why:  {fix.get('explanation', '')}")

    lines.append("\n" + "=" * 62)
    return "\n".join(lines)


def human_review(state: CodeReviewState) -> dict:
    # Pass the summary as the interrupt value — main.py prints it once
    feedback = interrupt(build_review_summary(state))
    return {"human_feedback": feedback}


# ── Node 9: Final Report ──────────────────────────────────────────────────────

def generate_final_report(state: CodeReviewState) -> dict:
    findings = state.get("synthesized_findings", [])
    suggestions = state.get("fix_suggestions", [])
    feedback = state.get("human_feedback", "approved")
    fix_map = {s["finding_id"]: s for s in suggestions if "finding_id" in s}

    severity_counts = {s: len([f for f in findings if f.get("severity") == s])
                       for s in ["critical", "high", "medium", "low"]}

    lines = [
        "",
        "=" * 62,
        "  CODEPILOT — FINAL CODE REVIEW REPORT",
        "=" * 62,
        f"  Reviewer feedback : {feedback}",
        f"  Total findings    : {len(findings)} "
        f"(critical: {severity_counts['critical']}, "
        f"high: {severity_counts['high']}, "
        f"medium: {severity_counts['medium']}, "
        f"low: {severity_counts['low']})",
    ]

    for sev in ["critical", "high", "medium", "low"]:
        tier = [f for f in findings if f.get("severity") == sev]
        if not tier:
            continue
        lines.append(f"\n  {sev.upper()}  ({len(tier)})")
        lines.append("  " + "-" * 40)
        for f in tier:
            line_ref = f" — line {f['line']}" if f.get("line") else ""
            lines.append(f"  [{f.get('type','?').upper()}]{line_ref}  {f.get('description','')}")
            fix = fix_map.get(f.get("id"))
            if fix:
                lines.append(f"    Fix: {fix.get('suggested_fix','')}")
                lines.append(f"    Why: {fix.get('explanation','')}")

    lines.append("\n" + "=" * 62)
    final_report = "\n".join(lines)
    print(final_report)
    return {"final_report": final_report}
