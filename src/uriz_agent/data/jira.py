"""Jira REST and export loaders."""

from __future__ import annotations

import base64
import csv
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from src.uriz_agent.schemas import JiraIssue

DEFAULT_JIRA_FIELDS = ["summary", "description", "status", "priority", "assignee", "issuetype", "labels", "parent"]


class JiraRestError(RuntimeError):
    """Raised when Jira REST cannot return issues with a useful diagnostic."""


def load_jira_issues(source: Path | None = None, project_key: str = "URIZ") -> list[JiraIssue]:
    """Load Jira issues from JSON/CSV export or Jira Cloud REST environment variables."""

    if source is not None:
        if not source.exists():
            raise FileNotFoundError(f"Jira source does not exist: {source}")
        if source.suffix.lower() == ".csv":
            return _load_csv(source)
        return _load_json(source)
    return _load_rest(project_key)


def check_jira_rest(project_key: str = "URIZ") -> dict[str, Any]:
    """Run a small live Jira REST check and return query diagnostics."""

    jql = _jira_jql(project_key)
    issues = _load_rest(project_key=project_key, max_results=10)
    return {
        "jql": jql,
        "issues_returned": len(issues),
        "issue_keys": [issue.key for issue in issues],
    }


def _load_json(path: Path) -> list[JiraIssue]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    records = data.get("issues", data) if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise ValueError("Jira JSON export must be a list or contain an 'issues' list.")
    return [_normalize_issue(record) for record in records]


def _load_csv(path: Path) -> list[JiraIssue]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [_normalize_issue(row) for row in csv.DictReader(handle)]


def _load_rest(project_key: str, max_results: int = 100) -> list[JiraIssue]:
    base_url = os.getenv("JIRA_BASE_URL", "").rstrip("/")
    email = os.getenv("JIRA_EMAIL", "")
    token = os.getenv("JIRA_API_TOKEN", "")
    jql = _jira_jql(project_key)
    if not all([base_url, email, token]):
        raise ValueError("Provide --jira-file or set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN.")

    auth = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        return _load_rest_enhanced_search(base_url, headers, jql, max_results)
    except JiraRestError as enhanced_error:
        try:
            return _load_rest_legacy_search(base_url, headers, jql, max_results)
        except JiraRestError as legacy_error:
            raise JiraRestError(
                "Jira REST search failed. The app tried the current enhanced search endpoint "
                "(/rest/api/3/search/jql) and the legacy search endpoint (/rest/api/3/search). "
                f"JQL used: {jql}. Enhanced error: {enhanced_error}. Legacy error: {legacy_error}"
            ) from legacy_error


def _jira_jql(project_key: str) -> str:
    # Jira Cloud UI now says "space", but Jira REST/JQL examples still use the `project` field.
    raw_jql = os.getenv("JIRA_JQL", f"project = {project_key} ORDER BY created DESC").strip()
    return _normalize_jira_jql(raw_jql)


def _normalize_jira_jql(jql: str) -> str:
    return re.sub(r"^\s*space\s*=\s*", "project = ", jql, count=1, flags=re.IGNORECASE)


def _load_rest_enhanced_search(base_url: str, headers: dict[str, str], jql: str, max_results: int) -> list[JiraIssue]:
    issues: list[JiraIssue] = []
    next_page_token: str | None = None
    while True:
        payload: dict[str, Any] = {
            "jql": jql,
            "maxResults": min(max_results, 100),
            "fields": DEFAULT_JIRA_FIELDS,
        }
        if next_page_token:
            payload["nextPageToken"] = next_page_token
        data = _request_json(
            f"{base_url}/rest/api/3/search/jql",
            headers=headers,
            method="POST",
            payload=payload,
        )
        issues.extend(_normalize_issue(record) for record in data.get("issues", []))
        next_page_token = data.get("nextPageToken")
        if not next_page_token or len(issues) >= max_results:
            return issues[:max_results]


def _load_rest_legacy_search(base_url: str, headers: dict[str, str], jql: str, max_results: int) -> list[JiraIssue]:
    query = urllib.parse.urlencode(
        {
            "jql": jql,
            "maxResults": str(max_results),
            "fields": ",".join(DEFAULT_JIRA_FIELDS),
        }
    )
    data = _request_json(f"{base_url}/rest/api/3/search?{query}", headers=headers, method="GET")
    return [_normalize_issue(record) for record in data.get("issues", [])]


def _request_json(url: str, headers: dict[str, str], method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=body, method=method)
    for key, value in headers.items():
        request.add_header(key, value)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        message = _jira_error_message(raw)
        raise JiraRestError(f"HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise JiraRestError(f"Network error: {exc.reason}") from exc


def _jira_error_message(raw: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw[:500]
    messages: list[str] = []
    if data.get("errorMessages"):
        messages.extend(str(item) for item in data["errorMessages"])
    if data.get("errors"):
        messages.extend(f"{key}: {value}" for key, value in data["errors"].items())
    return "; ".join(messages) or raw[:500]


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
