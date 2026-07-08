"""Jira REST and export loaders."""

from __future__ import annotations

import base64
import csv
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from src.uriz_agent.schemas import JiraIssue


def load_jira_issues(source: Path | None = None, project_key: str = "URIZ") -> list[JiraIssue]:
    """Load Jira issues from JSON/CSV export or Jira Cloud REST environment variables."""

    if source is not None:
        if not source.exists():
            raise FileNotFoundError(f"Jira source does not exist: {source}")
        if source.suffix.lower() == ".csv":
            return _load_csv(source)
        return _load_json(source)
    return _load_rest(project_key)


def _load_json(path: Path) -> list[JiraIssue]:
    data = json.loads(path.read_text(encoding="utf-8"))
    records = data.get("issues", data) if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise ValueError("Jira JSON export must be a list or contain an 'issues' list.")
    return [_normalize_issue(record) for record in records]


def _load_csv(path: Path) -> list[JiraIssue]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [_normalize_issue(row) for row in csv.DictReader(handle)]


def _load_rest(project_key: str) -> list[JiraIssue]:
    base_url = os.getenv("JIRA_BASE_URL", "").rstrip("/")
    email = os.getenv("JIRA_EMAIL", "")
    token = os.getenv("JIRA_API_TOKEN", "")
    jql = os.getenv("JIRA_JQL", f"project = {project_key} ORDER BY created DESC")
    if not all([base_url, email, token]):
        raise ValueError("Provide --jira-file or set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN.")

    query = urllib.parse.urlencode(
        {
            "jql": jql,
            "maxResults": "100",
            "fields": "summary,description,status,priority,assignee,issuetype,labels,parent",
        }
    )
    request = urllib.request.Request(f"{base_url}/rest/api/3/search?{query}")
    auth = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
    request.add_header("Authorization", f"Basic {auth}")
    request.add_header("Accept", "application/json")
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    return [_normalize_issue(record) for record in data.get("issues", [])]


def _normalize_issue(record: dict[str, Any]) -> JiraIssue:
    fields = record.get("fields", record)
    key = str(record.get("key") or fields.get("key") or fields.get("Issue key") or fields.get("Issue Key") or "").strip()
    if not key:
        raise ValueError(f"Jira record is missing an issue key: {record}")

    summary = _first_text(fields, ["summary", "Summary", "name", "Name"])
    description = _extract_description(fields.get("description") or fields.get("Description") or "")
    explicit_ac = fields.get("acceptance_criteria") or fields.get("Acceptance Criteria") or fields.get("customfield_acceptance_criteria")
    issue_type = _extract_name(fields.get("issuetype") or fields.get("Issue Type") or fields.get("issue_type") or "Story")
    status = _extract_name(fields.get("status") or fields.get("Status") or "")
    priority = _extract_name(fields.get("priority") or fields.get("Priority") or "")
    assignee = _extract_name(fields.get("assignee") or fields.get("Assignee") or "")
    labels = fields.get("labels") or fields.get("Labels") or []
    if isinstance(labels, str):
        labels = [label.strip() for label in labels.split(",") if label.strip()]
    parent = fields.get("parent") or fields.get("Parent") or None
    parent_key = parent.get("key") if isinstance(parent, dict) else (str(parent) if parent else None)

    return JiraIssue(
        key=key,
        issue_type=issue_type,
        summary=summary or key,
        description=description,
        status=status,
        priority=priority,
        assignee=assignee,
        acceptance_criteria=_normalize_acceptance_criteria(explicit_ac, description),
        labels=list(labels),
        parent_key=parent_key,
        raw=record,
    )


def _first_text(record: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = record.get(key)
        if value is not None:
            return _extract_description(value).strip()
    return ""


def _extract_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or value.get("displayName") or value.get("value") or value.get("key") or "")
    return str(value or "")


def _extract_description(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if value.get("type") == "text":
            return str(value.get("text", ""))
        parts: list[str] = []
        for child in value.get("content", []):
            text = _extract_description(child)
            if text:
                parts.append(text)
        return "\n".join(parts)
    if isinstance(value, list):
        return "\n".join(_extract_description(item) for item in value if item)
    return str(value or "")


def _normalize_acceptance_criteria(explicit_value: Any, description: str) -> list[str]:
    if isinstance(explicit_value, list):
        return [str(item).strip() for item in explicit_value if str(item).strip()]
    if isinstance(explicit_value, str) and explicit_value.strip():
        lines = [line.strip(" -\t") for line in explicit_value.splitlines()]
        return [line for line in lines if line]

    criteria: list[str] = []
    capture = False
    for raw_line in description.splitlines():
        line = raw_line.strip()
        lower = line.lower()
        if not line:
            continue
        if not capture and any(marker in lower for marker in ["acceptance criteria", "kriterijumi prihvatanja", "ac:"]):
            capture = True
            continue
        if capture and (line.startswith(("-", "*")) or lower.startswith(("given", "when", "then", "and"))):
            criteria.append(line.strip(" -*\t"))
        elif capture and len(criteria) < 5 and not lower.endswith(":"):
            criteria.append(line)
    return criteria


