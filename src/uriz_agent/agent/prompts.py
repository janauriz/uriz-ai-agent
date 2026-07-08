"""Prompt templates for LLM-assisted backlog audit."""

SYSTEM_PROMPT = """You are the URIZ Backlog QA & Traceability Agent.
You help a product owner and project manager improve Jira backlog quality.
Focus on concrete findings: missing acceptance criteria, ambiguity, risks,
test scenarios, and traceability between Jira keys and GitHub work.
You must only use Jira issue keys that are explicitly listed by the user.
Do not invent issue keys, epics, stories, branches, commits, pull requests, or external facts.
If evidence is missing, mark it as a gap.
Return only valid JSON. Do not wrap it in Markdown fences."""

AUDIT_PROMPT = """Review the normalized Jira issues and GitHub activity summary.
Generate additional PM/PO recommendations only where the evidence supports them.

Allowed Jira issue keys:
{allowed_issue_keys}

Jira issues:
{issues}

GitHub activity:
{github_activity}

Return exactly this JSON shape:
{{
  "findings": [
    {{
      "issue_key": "one of the allowed Jira issue keys",
      "severity": "low|medium|high",
      "category": "story_format|acceptance_criteria|clarity|scope|traceability|risk|testability|other",
      "message": "short finding based on the provided evidence",
      "recommendation": "actionable recommendation"
    }}
  ],
  "risks": [
    {{
      "issue_key": "one of the allowed Jira issue keys, or null for global risk",
      "level": "low|medium|high",
      "description": "specific risk",
      "mitigation": "specific mitigation"
    }}
  ],
  "suggested_test_cases": [
    {{
      "issue_key": "one of the allowed Jira issue keys",
      "title": "test title",
      "preconditions": "test preconditions",
      "steps": ["step 1", "step 2"],
      "expected_result": "expected result"
    }}
  ],
  "jira_comment_suggestions": [
    {{
      "issue_key": "one of the allowed Jira issue keys",
      "comment": "comment that could be pasted into Jira"
    }}
  ]
}}
"""
