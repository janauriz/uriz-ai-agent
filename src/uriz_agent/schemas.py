"""Pydantic schemas for normalized inputs and structured audit output."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class JiraIssue(BaseModel):
    key: str
    issue_type: str = "Story"
    summary: str
    description: str = ""
    status: str = ""
    priority: str = ""
    assignee: str = ""
    acceptance_criteria: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    parent_key: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class GitCommit(BaseModel):
    hash: str
    message: str
    author: str = ""
    date: str = ""


class PullRequest(BaseModel):
    title: str
    body: str = ""
    url: str = ""
    state: str = ""


class GitActivity(BaseModel):
    branches: list[str] = Field(default_factory=list)
    commits: list[GitCommit] = Field(default_factory=list)
    pull_requests: list[PullRequest] = Field(default_factory=list)


class StoryFinding(BaseModel):
    issue_key: str
    severity: str
    category: str
    message: str
    recommendation: str


class Risk(BaseModel):
    issue_key: str | None = None
    level: str
    description: str
    mitigation: str


class TestCase(BaseModel):
    issue_key: str
    title: str
    preconditions: str = ""
    steps: list[str] = Field(default_factory=list)
    expected_result: str


class TraceabilityGap(BaseModel):
    issue_key: str
    reason: str
    recommendation: str


class JiraCommentSuggestion(BaseModel):
    issue_key: str
    comment: str


class AuditReport(BaseModel):
    run_id: str
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    summary: str
    issues_analyzed: int
    story_quality_score: int = Field(ge=0, le=100)
    traceability_score: int = Field(ge=0, le=100)
    findings: list[StoryFinding] = Field(default_factory=list)
    risks: list[Risk] = Field(default_factory=list)
    missing_acceptance_criteria: list[StoryFinding] = Field(default_factory=list)
    suggested_test_cases: list[TestCase] = Field(default_factory=list)
    jira_comment_suggestions: list[JiraCommentSuggestion] = Field(default_factory=list)
    github_linkage_gaps: list[TraceabilityGap] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

