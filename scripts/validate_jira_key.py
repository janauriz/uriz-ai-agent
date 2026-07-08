"""Validate that text contains a URIZ Jira issue key."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DEFAULT_PATTERN = r"URIZ-\d+"


def contains_jira_key(text: str, pattern: str = DEFAULT_PATTERN) -> bool:
    return re.search(pattern, text) is not None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a Jira key in text or a commit message file.")
    parser.add_argument("source", help="Text to validate, or path to a commit message file.")
    parser.add_argument("--pattern", default=DEFAULT_PATTERN, help="Regex pattern for accepted Jira keys.")
    args = parser.parse_args(argv)

    source_path = Path(args.source)
    text = source_path.read_text(encoding="utf-8") if source_path.exists() else args.source

    if contains_jira_key(text, args.pattern):
        return 0

    print(f"Missing Jira key. Expected a key matching {args.pattern}, e.g. URIZ-123.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

