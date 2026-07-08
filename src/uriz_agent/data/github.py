"""Local Git and optional pull request metadata loader."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from src.uriz_agent.schemas import GitActivity, GitCommit, PullRequest


def load_git_activity(repo_dir: Path, pr_file: Path | None = None) -> GitActivity:
    branches = _git_lines(repo_dir, ["branch", "--all", "--format", "%(refname:short)"])
    commits = _load_commits(repo_dir)
    pull_requests = _load_pull_requests(pr_file) if pr_file else []
    return GitActivity(branches=branches, commits=commits, pull_requests=pull_requests)


def extract_issue_keys(text: str, project_key: str = "URIZ") -> set[str]:
    return set(re.findall(rf"\b{re.escape(project_key)}-\d+\b", text or ""))


def issue_keys_in_activity(activity: GitActivity, project_key: str = "URIZ") -> set[str]:
    keys: set[str] = set()
    for branch in activity.branches:
        keys.update(extract_issue_keys(branch, project_key))
    for commit in activity.commits:
        keys.update(extract_issue_keys(commit.message, project_key))
    for pr in activity.pull_requests:
        keys.update(extract_issue_keys(f"{pr.title}\n{pr.body}", project_key))
    return keys


def _load_commits(repo_dir: Path) -> list[GitCommit]:
    lines = _git_lines(repo_dir, ["log", "--pretty=format:%H%x1f%an%x1f%ad%x1f%s", "--date=iso", "-n", "50"])
    commits: list[GitCommit] = []
    for line in lines:
        parts = line.split("\x1f", 3)
        if len(parts) == 4:
            commits.append(GitCommit(hash=parts[0], author=parts[1], date=parts[2], message=parts[3]))
    return commits


def _load_pull_requests(path: Path) -> list[PullRequest]:
    if not path.exists():
        raise FileNotFoundError(f"Pull request metadata file does not exist: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    records = data.get("pull_requests", data) if isinstance(data, dict) else data
    return [PullRequest(**record) for record in records]


def _git_lines(repo_dir: Path, args: list[str]) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_dir), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]

