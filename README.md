# URIZ Backlog QA & Traceability Agent

Python CLI agent for auditing Jira backlog quality and Jira/GitHub traceability. It is designed for the URIZ seminar project and the first/third homework requirements: defined input data, multi-step agent workflow, LLM integration point, external service data, structured output, tests, and documentation.

## What The Agent Does

The agent reads Jira work items and GitHub/local Git activity, then generates:

- story quality score,
- traceability score,
- missing acceptance criteria,
- risks and mitigations,
- suggested test cases,
- Jira comment suggestions,
- GitHub linkage gaps.

It is not a generic chatbot. It runs a fixed PM/PO workflow and writes JSON + Markdown reports.

## Architecture

```text
Jira REST/export + Git metadata
        |
        v
load_sources -> normalize_backlog -> analyze_story_quality
        -> analyze_traceability -> generate_recommendations -> write reports
```

The workflow uses LangGraph when installed. If LangGraph is not installed, the same nodes run through a deterministic sequential fallback so offline tests and demos still work. OpenAI is used through `langchain-openai` when `--use-llm` and `OPENAI_API_KEY` are provided.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` with real values only locally. Do not commit `.env`.

## Commands

Check configuration:

```powershell
python main.py doctor
```

Run offline sample audit:

```powershell
python main.py audit --jira-file tests\fixtures\jira_export.json --github-pr-file tests\fixtures\pull_requests.json --github-dir . --output-dir reports
```

Run with Jira REST:

```powershell
python main.py audit --github-dir . --output-dir reports
```

Run with OpenAI-assisted recommendations:

```powershell
python main.py audit --jira-file tests\fixtures\jira_export.json --github-dir . --use-llm
```

Copy sample data:

```powershell
python main.py sample-data --target-dir sample-data
```

## Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for LLM-assisted analysis.
- `OPENAI_MODEL`: defaults to `gpt-5.4-mini`; use `gpt-5.5` for a stronger final run.
- `JIRA_BASE_URL`: Jira Cloud base URL.
- `JIRA_EMAIL`: Jira account email.
- `JIRA_API_TOKEN`: Jira API token.
- `JIRA_JQL`: optional query, defaults to `project = URIZ ORDER BY created DESC`.

## Jira/GitHub Rules

- Jira project key: `URIZ`.
- Branch: `URIZ-123-short-description`.
- Commit: `URIZ-123: concise change summary`.
- PR title: `URIZ-123: concise PR title`.

Install the commit-msg hook:

```powershell
Copy-Item tools\git-hooks\commit-msg .git\hooks\commit-msg
```

## Tests

```powershell
python -m unittest discover -s tests
```

The tests use fixture data and do not require network access.

## Limitations

- Jira REST requires valid Jira Cloud credentials.
- PR analysis is file-based unless PR metadata is exported to JSON.
- LLM output is optional and intentionally separated from deterministic rules to keep demos repeatable.
- Optional Ollama provider support is planned after the OpenAI/LangChain path is stable.

