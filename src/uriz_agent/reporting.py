"""Report writers for JSON and Markdown audit output."""

from __future__ import annotations

import json
from pathlib import Path

from src.uriz_agent.schemas import AuditReport


def write_report_bundle(report: AuditReport, output_dir: Path) -> dict[str, Path]:
    run_dir = output_dir / report.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_dir / "audit.json"
    markdown_path = run_dir / "audit.md"
    json_path.write_text(json.dumps(report.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}


def render_markdown(report: AuditReport) -> str:
    lines = [
        "# URIZ Backlog QA & Traceability Audit",
        "",
        f"Run ID: `{report.run_id}`",
        f"Generated at: `{report.generated_at}`",
        "",
        "## Summary",
        "",
        report.summary,
        "",
        f"- Issues analyzed: {report.issues_analyzed}",
        f"- Story quality score: {report.story_quality_score}/100",
        f"- Traceability score: {report.traceability_score}/100",
        "",
        "## Findings",
        "",
    ]
    lines.extend(_finding_lines(report.findings))
    lines.extend(["", "## Missing Acceptance Criteria", ""])
    lines.extend(_finding_lines(report.missing_acceptance_criteria))
    lines.extend(["", "## Risks", ""])
    if report.risks:
        for risk in report.risks:
            issue = f"`{risk.issue_key}` " if risk.issue_key else ""
            lines.append(f"- {issue}**{risk.level}**: {risk.description} Mitigation: {risk.mitigation}")
    else:
        lines.append("- No risks detected by the current rules.")
    lines.extend(["", "## Suggested Test Cases", ""])
    for test_case in report.suggested_test_cases:
        lines.append(f"### {test_case.issue_key}: {test_case.title}")
        if test_case.preconditions:
            lines.append(f"Preconditions: {test_case.preconditions}")
        for index, step in enumerate(test_case.steps, 1):
            lines.append(f"{index}. {step}")
        lines.append(f"Expected result: {test_case.expected_result}")
        lines.append("")
    lines.extend(["## Traceability Gaps", ""])
    if report.github_linkage_gaps:
        for gap in report.github_linkage_gaps:
            lines.append(f"- `{gap.issue_key}`: {gap.reason} Recommendation: {gap.recommendation}")
    else:
        lines.append("- No Jira/GitHub traceability gaps detected.")
    lines.extend(["", "## Jira Comment Suggestions", ""])
    if report.jira_comment_suggestions:
        for suggestion in report.jira_comment_suggestions:
            lines.append(f"- `{suggestion.issue_key}`: {suggestion.comment}")
    else:
        lines.append("- No Jira comments suggested.")
    lines.extend(["", "## Metadata", "", "```json", json.dumps(report.metadata, ensure_ascii=False, indent=2), "```", ""])
    return "\n".join(lines)


def _finding_lines(findings: list) -> list[str]:
    if not findings:
        return ["- No findings in this category."]
    return [
        f"- `{finding.issue_key}` **{finding.severity} / {finding.category}**: "
        f"{finding.message} Recommendation: {finding.recommendation}"
        for finding in findings
    ]

