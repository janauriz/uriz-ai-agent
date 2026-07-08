# Initial Jira Backlog

Use Jira space key / issue key prefix `URIZ` and the workflow:

`Backlog -> Selected -> In Progress -> In Review -> Done`

Jira Cloud may use the word **space** in the UI. In JQL and REST examples, use the key through the `project` field:

```jql
project = URIZ ORDER BY created DESC
```

## Components

- Agent Core
- JIRA Integration
- GitHub Integration
- Reporting
- Documentation
- Evaluation
- Governance

## Current Epics

| Key | Type | Summary | Component | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| URIZ-4 | Epic | Project setup, rules, and documentation scaffold | Governance | Repo has README, CONTRIBUTING, PR template, Jira-key hook, SRS map. |
| URIZ-5 | Epic | JIRA and GitHub data ingestion | JIRA Integration, GitHub Integration | Agent can read Jira export/REST and local Git metadata. |
| URIZ-6 | Epic | LangGraph agent workflow | Agent Core | Workflow has load, normalize, story quality, traceability, recommendation, report steps. |
| URIZ-7 | Epic | Structured report generation | Reporting | Agent writes JSON and Markdown outputs. |
| URIZ-8 | Epic | Evaluation on sample inputs | Evaluation | Three sample input classes are audited and validated. |
| URIZ-9 | Epic | SRS and seminar documentation | Documentation | Template 2026 and repo docs explain problem, users, requirements, workflow, tests, limitations. |

## Current Stories

| Key | Parent Epic | Story | User Value | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| URIZ-10 | URIZ-4 | Set up repository governance and Jira/GitHub traceability rules | As a PM, I want repository rules so every code change can be traced to Jira. | README, PR template, commit validator, and naming rules exist. |
| URIZ-11 | URIZ-5 | Load Jira export and REST data | As a PO, I want backlog data loaded from Jira so the agent can audit real work items. | JSON/CSV exports and Jira REST inputs normalize to the same schema. |
| URIZ-12 | URIZ-6 | Analyze story quality | As a PO, I want weak stories identified before sprint planning. | Output flags missing AC, vague wording, oversized scope, and missing NFRs. |
| URIZ-13 | URIZ-6 | Analyze Jira/GitHub traceability | As a PM, I want to know which Jira tasks have no GitHub evidence. | Output lists issues without branch, commit, or PR references. |
| URIZ-14 | URIZ-7 | Generate structured reports | As a QA/team member, I want readable and machine-readable reports. | Markdown and JSON include summary, scores, risks, test ideas, and comments. |
| URIZ-15 | URIZ-9 | Keep SRS and repository docs aligned | As a student team, we want homework and seminar artifacts to describe the same product. | SRS map and traceability matrix match Jira and code. |
