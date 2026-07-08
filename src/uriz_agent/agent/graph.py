"""LangGraph workflow and deterministic audit implementation."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, TypedDict
from uuid import uuid4

from src.uriz_agent.agent.prompts import AUDIT_PROMPT, SYSTEM_PROMPT
from src.uriz_agent.data.github import issue_keys_in_activity, load_git_activity
from src.uriz_agent.data.jira import load_jira_issues
from src.uriz_agent.schemas import (
    AuditReport,
    GitActivity,
    JiraCommentSuggestion,
    JiraIssue,
    Risk,
    StoryFinding,
    TestCase,
    TraceabilityGap,
)


class AuditState(TypedDict, total=False):
    jira_file: Path | None
    github_dir: Path
    github_pr_file: Path | None
    project_key: str
    use_llm: bool
    run_id: str
    issues: list[JiraIssue]
    git_activity: GitActivity
    findings: list[StoryFinding]
    risks: list[Risk]
    missing_acceptance_criteria: list[StoryFinding]
    suggested_test_cases: list[TestCase]
    jira_comment_suggestions: list[JiraCommentSuggestion]
    github_linkage_gaps: list[TraceabilityGap]
    story_quality_score: int
    traceability_score: int
    report: AuditReport


class SequentialWorkflow:
    """Small fallback runner used when LangGraph is not installed."""

    def __init__(self, nodes: list[Any]) -> None:
        self._nodes = nodes

    def invoke(self, state: AuditState) -> AuditState:
        current = state
        for node in self._nodes:
            current.update(node(current))
        return current


def run_audit(
    jira_file: Path | None,
    github_dir: Path,
    github_pr_file: Path | None = None,
    project_key: str = "URIZ",
    use_llm: bool = False,
    run_id: str | None = None,
) -> AuditReport:
    graph = build_workflow()
    final_state = graph.invoke(
        {
            "jira_file": jira_file,
            "github_dir": github_dir,
            "github_pr_file": github_pr_file,
            "project_key": project_key,
            "use_llm": use_llm,
            "run_id": run_id or f"run-{uuid4().hex[:8]}",
        }
    )
    return final_state["report"]


def build_workflow() -> Any:
    nodes = [load_sources, normalize_backlog, analyze_story_quality, analyze_traceability, generate_recommendations, build_report]
    try:
        from langgraph.graph import END, START, StateGraph

        workflow = StateGraph(AuditState)
        for node in nodes:
            workflow.add_node(node.__name__, node)
        workflow.add_edge(START, "load_sources")
        workflow.add_edge("load_sources", "normalize_backlog")
        workflow.add_edge("normalize_backlog", "analyze_story_quality")
        workflow.add_edge("analyze_story_quality", "analyze_traceability")
        workflow.add_edge("analyze_traceability", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "build_report")
        workflow.add_edge("build_report", END)
        return workflow.compile()
    except ImportError:
        return SequentialWorkflow(nodes)


def load_sources(state: AuditState) -> AuditState:
    issues = load_jira_issues(state.get("jira_file"), state.get("project_key", "URIZ"))
    git_activity = load_git_activity(state.get("github_dir", Path(".")), state.get("github_pr_file"))
    return {"issues": issues, "git_activity": git_activity}


def normalize_backlog(state: AuditState) -> AuditState:
    issues = sorted(state["issues"], key=lambda issue: issue.key)
    return {"issues": issues}


def analyze_story_quality(state: AuditState) -> AuditState:
    findings: list[StoryFinding] = []
    missing_ac: list[StoryFinding] = []
    risks: list[Risk] = []
    total_penalty = 0

    for issue in state["issues"]:
        issue_penalty = 0
        text = f"{issue.summary}\n{issue.description}".lower()
        if issue.issue_type.lower() in {"story", "user story"} and not _has_user_story_shape(issue):
            findings.append(
                StoryFinding(
                    issue_key=issue.key,
                    severity="medium",
                    category="story_format",
                    message="Story does not clearly express role, need, and value.",
                    recommendation="Rewrite as: As a <role>, I want <capability>, so that <benefit>.",
                )
            )
            issue_penalty += 12
        if not issue.acceptance_criteria:
            finding = StoryFinding(
                issue_key=issue.key,
                severity="high",
                category="acceptance_criteria",
                message="Acceptance criteria are missing.",
                recommendation="Add 2-5 verifiable Given/When/Then or checklist criteria.",
            )
            findings.append(finding)
            missing_ac.append(finding)
            issue_penalty += 20
        if _contains_vague_terms(text):
            findings.append(
                StoryFinding(
                    issue_key=issue.key,
                    severity="medium",
                    category="clarity",
                    message="Description uses vague terms that are hard to test.",
                    recommendation="Replace vague wording with measurable behavior, thresholds, or examples.",
                )
            )
            issue_penalty += 8
        if _looks_oversized(issue):
            findings.append(
                StoryFinding(
                    issue_key=issue.key,
                    severity="medium",
                    category="scope",
                    message="Issue appears broad and may be too large for a focused implementation task.",
                    recommendation="Split into smaller stories or subtasks with separate acceptance criteria.",
                )
            )
            issue_penalty += 8
        if _has_security_or_data_terms(text) and "security" not in " ".join(issue.labels).lower():
            risks.append(
                Risk(
                    issue_key=issue.key,
                    level="medium",
                    description="Issue touches credentials, tokens, users, or external data without an explicit security label.",
                    mitigation="Add security/privacy acceptance criteria and verify no secrets are stored in code or reports.",
                )
            )
            issue_penalty += 5
        total_penalty += min(issue_penalty, 35)

    max_penalty = max(len(state["issues"]) * 35, 1)
    score = max(0, round(100 - (total_penalty / max_penalty) * 100))
    return {
        "findings": findings,
        "missing_acceptance_criteria": missing_ac,
        "risks": risks,
        "story_quality_score": score,
    }


def analyze_traceability(state: AuditState) -> AuditState:
    project_key = state.get("project_key", "URIZ")
    linked_keys = issue_keys_in_activity(state["git_activity"], project_key)
    gaps: list[TraceabilityGap] = []
    auditable_issues = [issue for issue in state["issues"] if issue.issue_type.lower() not in {"epic"}]
    for issue in auditable_issues:
        if issue.key not in linked_keys:
            gaps.append(
                TraceabilityGap(
                    issue_key=issue.key,
                    reason="No matching Jira key found in local branches, recent commits, or PR metadata.",
                    recommendation=f"Use branch, commit, and PR names containing {issue.key}.",
                )
            )
    linked_count = max(len(auditable_issues) - len(gaps), 0)
    score = round((linked_count / len(auditable_issues)) * 100) if auditable_issues else 100
    return {"github_linkage_gaps": gaps, "traceability_score": score}


def generate_recommendations(state: AuditState) -> AuditState:
    test_cases = [_test_case_for_issue(issue) for issue in state["issues"] if issue.issue_type.lower() not in {"epic"}]
    comments = [
        JiraCommentSuggestion(
            issue_key=finding.issue_key,
            comment=f"Backlog QA finding: {finding.message} Recommendation: {finding.recommendation}",
        )
        for finding in state.get("findings", [])
    ]

    extra_risks = _llm_risks_if_available(state) if state.get("use_llm") else []
    return {
        "suggested_test_cases": test_cases,
        "jira_comment_suggestions": comments,
        "risks": [*state.get("risks", []), *extra_risks],
    }


def build_report(state: AuditState) -> AuditState:
    issues = state["issues"]
    summary = (
        f"Analyzed {len(issues)} Jira issue(s). "
        f"Story quality score is {state['story_quality_score']}/100 and "
        f"traceability score is {state['traceability_score']}/100."
    )
    report = AuditReport(
        run_id=state["run_id"],
        summary=summary,
        issues_analyzed=len(issues),
        story_quality_score=state["story_quality_score"],
        traceability_score=state["traceability_score"],
        findings=state.get("findings", []),
        risks=state.get("risks", []),
        missing_acceptance_criteria=state.get("missing_acceptance_criteria", []),
        suggested_test_cases=state.get("suggested_test_cases", []),
        jira_comment_suggestions=state.get("jira_comment_suggestions", []),
        github_linkage_gaps=state.get("github_linkage_gaps", []),
        metadata={
            "project_key": state.get("project_key", "URIZ"),
            "llm_requested": state.get("use_llm", False),
            "branches_scanned": len(state["git_activity"].branches),
            "commits_scanned": len(state["git_activity"].commits),
            "pull_requests_scanned": len(state["git_activity"].pull_requests),
        },
    )
    return {"report": report}


def _llm_risks_if_available(state: AuditState) -> list[Risk]:
    if not os.getenv("OPENAI_API_KEY"):
        return []
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        return []

    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
    llm = ChatOpenAI(model=model, temperature=float(os.getenv("OPENAI_TEMPERATURE", "0")))
    issue_payload = [issue.model_dump(exclude={"raw"}) for issue in state["issues"][:8]]
    git_payload = state["git_activity"].model_dump()
    prompt = AUDIT_PROMPT.format(
        issues=json.dumps(issue_payload, ensure_ascii=False, indent=2),
        github_activity=json.dumps(git_payload, ensure_ascii=False, indent=2),
    )
    response = llm.invoke([("system", SYSTEM_PROMPT), ("human", prompt)])
    text = getattr(response, "content", "")
    if not text:
        return []
    return [
        Risk(
            issue_key=None,
            level="low",
            description="LLM-assisted review produced additional qualitative guidance.",
            mitigation=str(text)[:900],
        )
    ]


def _has_user_story_shape(issue: JiraIssue) -> bool:
    text = f"{issue.summary} {issue.description}".lower()
    english = all(token in text for token in ["as a", "i want", "so that"])
    serbian = any(token in text for token in ["kao ", "zelim", "želim", "kako bih", "da bih"])
    return english or serbian


def _contains_vague_terms(text: str) -> bool:
    return bool(re.search(r"\b(simple|easy|fast|quick|better|improve|optimize|etc\.?|and so on|user friendly)\b", text))


def _looks_oversized(issue: JiraIssue) -> bool:
    text = f"{issue.summary}\n{issue.description}"
    conjunction_count = len(re.findall(r"\b(and|or|i|ili|kao i)\b", text.lower()))
    return len(text) > 900 or conjunction_count > 10


def _has_security_or_data_terms(text: str) -> bool:
    return any(term in text for term in ["token", "api key", "password", "credential", "secret", "personal data", "email"])


def _test_case_for_issue(issue: JiraIssue) -> TestCase:
    first_ac = issue.acceptance_criteria[0] if issue.acceptance_criteria else "Defined acceptance criteria are satisfied."
    return TestCase(
        issue_key=issue.key,
        title=f"Validate {issue.summary}",
        preconditions=f"Jira issue {issue.key} is selected for implementation and relevant input data is available.",
        steps=[
            "Prepare representative input data for the issue.",
            "Run the related agent workflow or feature.",
            "Compare the result against the issue acceptance criteria.",
        ],
        expected_result=first_ac,
    )

