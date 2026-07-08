# Contributing

This project uses Jira-first development so that the seminar backlog, GitHub activity, and documentation stay aligned.

## Workflow

1. Pick or create a Jira work item in the Jira space with key `URIZ`.
2. Create a branch named `URIZ-123-short-description`.
3. Make focused changes with commits named `URIZ-123: concise summary`.
4. Run tests and an offline agent audit when relevant.
5. Open a PR titled `URIZ-123: concise summary`.
6. Include the Jira link/key, test evidence, and documentation impact in the PR body.

## Jira Structure

- Epics: large project outcomes such as agent workflow, integrations, reporting, evaluation, documentation.
- Stories: user-visible capabilities, written from PM/PO/QA/team-member perspective.
- Tasks: implementation work needed for a story.
- Subtasks: small technical steps that can be verified independently.

## Definition Of Done

- Jira issue has a clear description and acceptance criteria.
- Branch, commits, and PR all include the Jira key.
- Tests are run or a clear reason is documented.
- README/SRS/traceability docs are updated when behavior changes.
- No secrets or local `.env` values are committed.

## Local Hook Setup

Install the commit message validator:

```powershell
Copy-Item tools\git-hooks\commit-msg .git\hooks\commit-msg
```

The hook rejects commit messages that do not contain an issue key matching `URIZ-\d+`.


