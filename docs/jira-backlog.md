# Initial Jira Backlog

Use Jira space key / issue key prefix `URIZ` and create a software space with workflow:

`Backlog -> Selected -> In Progress -> In Review -> Done`

## Components

- Agent Core
- JIRA Integration
- GitHub Integration
- Reporting
- Documentation
- Evaluation
- Governance

## Epics And Starter Work Items

| Key | Type | Summary | Component | Acceptance Criteria |
| --- | --- | --- | --- | --- |
| URIZ-1 | Epic | Project setup, rules, documentation scaffold | Governance | Repo has README, CONTRIBUTING, PR template, Jira-key hook, SRS map. |
| URIZ-2 | Epic | JIRA/GitHub data ingestion | JIRA Integration, GitHub Integration | Agent can read Jira export/REST and local Git metadata. |
| URIZ-3 | Epic | LangGraph agent workflow | Agent Core | Workflow has load, normalize, story quality, traceability, recommendation, report steps. |
| URIZ-4 | Epic | Structured report generation | Reporting | Agent writes JSON and Markdown outputs. |
| URIZ-5 | Epic | Evaluation on 3 examples | Evaluation | Three sample inputs are audited and validated. |
| URIZ-6 | Epic | SRS and seminar documentation | Documentation | Template 2026 and repo docs explain problem, users, requirements, workflow, tests, limitations. |

## Suggested Stories

| Parent | Story | User Value | Acceptance Criteria |
| --- | --- | --- | --- |
| URIZ-2 | Import Jira export file | As a PO, I want to audit a backlog without live Jira access. | JSON and CSV exports load into normalized issues. |
| URIZ-2 | Import local Git activity | As a PM, I want to see whether work is linked to Jira. | Branches and recent commits are scanned for `URIZ-*` keys. |
| URIZ-3 | Analyze story quality | As a PO, I want weak stories identified before sprint planning. | Output flags missing AC, vague wording, oversized scope, and missing NFRs. |
| URIZ-3 | Analyze traceability | As a PM, I want to know which Jira tasks have no GitHub evidence. | Output lists issues without branches/commits/PR references. |
| URIZ-4 | Generate Markdown report | As a team member, I want a readable report. | Markdown includes summary, scores, risks, test ideas, and Jira comment suggestions. |
| URIZ-5 | Evaluate sample cases | As an examiner, I want proof that the agent works on multiple inputs. | Three fixtures cover weak story, linked story, and risk/security gap. |


