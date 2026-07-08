# URIZ Agent Development Rules

This repository implements the URIZ Backlog QA & Traceability Agent. Keep every code, documentation, and test change traceable to Jira work.

## Jira And Git Rules

- Jira space key / issue key prefix is `URIZ`.
- Branch names must include a Jira key, for example `URIZ-123-story-quality-audit`.
- Commit messages must include a Jira key, for example `URIZ-123: add Jira export parser`.
- Pull request titles must include a Jira key, for example `URIZ-123: add traceability report`.
- One PR should map to one primary Jira task/story whenever possible. Mention related keys in the PR body.
- No code-linked work is considered done until the Jira issue has acceptance criteria and the PR lists tests.

## Implementation Rules

- Keep the agent as a workflow-driven CLI, not a generic chatbot.
- Use structured input models, structured output models, and deterministic fallback behavior for demos without API keys.
- Keep OpenAI and Jira credentials in `.env`; never hardcode secrets.
- Prefer small modules under `src/uriz_agent/` over logic in `main.py`.
- Reports must be written as both JSON and Markdown.
- Sample data and tests must run without network access.

## Verification

- Run `python -m unittest discover -s tests` before marking a code task done.
- Run `python main.py doctor` after dependency or configuration changes.
- Run at least one offline demo:
  `python main.py audit --jira-file tests/fixtures/jira_export.json --github-dir . --output-dir reports/demo`


