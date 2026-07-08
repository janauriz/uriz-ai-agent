"""CLI entry point for the URIZ Backlog QA & Traceability Agent."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from src.uriz_agent.agent.graph import run_audit
from src.uriz_agent.config import load_environment
from src.uriz_agent.data.jira import JiraRestError, _jira_jql, check_jira_rest
from src.uriz_agent.reporting import write_report_bundle


DEFAULT_PROJECT_KEY = "URIZ"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="uriz-agent",
        description="Audit Jira backlog quality and Jira/GitHub traceability.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="Run a backlog and traceability audit.")
    audit.add_argument("--jira-file", type=Path, help="Path to Jira JSON/CSV export. If omitted, Jira REST env vars are used.")
    audit.add_argument("--github-dir", type=Path, default=Path("."), help="Path to the local Git repository.")
    audit.add_argument("--github-pr-file", type=Path, help="Optional JSON export with pull request metadata.")
    audit.add_argument("--output-dir", type=Path, default=Path("reports"), help="Directory where reports are written.")
    audit.add_argument("--run-id", help="Optional stable run id.")
    audit.add_argument("--project-key", default=DEFAULT_PROJECT_KEY, help="Jira space key / issue key prefix used for traceability checks.")
    audit.add_argument("--use-llm", action="store_true", help="Use OpenAI through LangChain when OPENAI_API_KEY is set.")
    audit.add_argument("--no-llm", action="store_true", help="Force deterministic offline analysis.")

    sample = subparsers.add_parser("sample-data", help="Copy sample Jira data into a target directory.")
    sample.add_argument("--target-dir", type=Path, default=Path("sample-data"), help="Target directory for copied fixtures.")

    jira_check = subparsers.add_parser("jira-check", help="Validate Jira REST credentials and JQL without running a full audit.")
    jira_check.add_argument("--project-key", default=DEFAULT_PROJECT_KEY, help="Jira space key / issue key prefix to use in the default JQL.")

    subparsers.add_parser("doctor", help="Check local configuration and optional dependencies.")

    return parser


def command_audit(args: argparse.Namespace) -> int:
    load_environment()
    use_llm = args.use_llm and not args.no_llm
    try:
        report = run_audit(
            jira_file=args.jira_file,
            github_dir=args.github_dir,
            github_pr_file=args.github_pr_file,
            project_key=args.project_key,
            use_llm=use_llm,
            run_id=args.run_id,
        )
    except (JiraRestError, ValueError) as exc:
        print(f"Jira input error: {exc}", file=sys.stderr)
        return 1
    outputs = write_report_bundle(report, args.output_dir)
    print(f"Audit complete: {outputs['markdown']}")
    print(f"JSON report: {outputs['json']}")
    print(f"Story quality score: {report.story_quality_score}")
    print(f"Traceability score: {report.traceability_score}")
    print(f"Issues analyzed: {report.issues_analyzed}")
    return 0


def command_sample_data(args: argparse.Namespace) -> int:
    source = Path(__file__).resolve().parent / "tests" / "fixtures" / "jira_export.json"
    args.target_dir.mkdir(parents=True, exist_ok=True)
    destination = args.target_dir / "jira_export.json"
    shutil.copyfile(source, destination)
    print(f"Sample Jira export copied to {destination}")
    return 0


def command_jira_check(args: argparse.Namespace) -> int:
    load_environment()
    try:
        result = check_jira_rest(args.project_key)
    except (JiraRestError, ValueError) as exc:
        print(f"Jira check failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


def command_doctor(_: argparse.Namespace) -> int:
    load_environment()
    checks = {
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
        "JIRA_BASE_URL": bool(os.getenv("JIRA_BASE_URL")),
        "JIRA_EMAIL": bool(os.getenv("JIRA_EMAIL")),
        "JIRA_API_TOKEN": bool(os.getenv("JIRA_API_TOKEN")),
        "JIRA_JQL": _jira_jql(DEFAULT_PROJECT_KEY),
    }
    optional_modules = ["pydantic", "langgraph", "langchain_openai", "dotenv"]
    module_status: dict[str, bool] = {}
    for module_name in optional_modules:
        try:
            __import__(module_name)
            module_status[module_name] = True
        except ImportError:
            module_status[module_name] = False

    print(json.dumps({"env": checks, "modules": module_status}, indent=2))
    if not module_status["pydantic"]:
        print("pydantic is required. Install dependencies from requirements.txt.", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "audit":
        return command_audit(args)
    if args.command == "sample-data":
        return command_sample_data(args)
    if args.command == "jira-check":
        return command_jira_check(args)
    if args.command == "doctor":
        return command_doctor(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
