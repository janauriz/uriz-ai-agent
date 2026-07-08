# SRS Content Map

This map keeps `Template 2026.docx`, Jira, and the repository aligned.

| SRS Section | Content For This Project | Repo Evidence |
| --- | --- | --- |
| Introduction | URIZ Backlog QA & Traceability Agent overview. | `README.md`, `docs/jira-backlog.md` |
| Aim and purpose | Automate PM/PO checks for story quality, risks, test ideas, and Jira/GitHub traceability. | `README.md`, `src/uriz_agent/agent/graph.py` |
| Users | Product owner, project manager, QA engineer, developer/team member. | `docs/traceability-matrix.md` |
| Project scope | CLI MVP with Jira export/REST, local Git scan, structured reports, sample fixtures. | `main.py`, `src/uriz_agent/` |
| Globalni opis resenja | Data loaders, LangGraph workflow, LLM/fallback analysis, report writer. | `src/uriz_agent/agent/graph.py` |
| Opis funkcionalnosti | Import data, normalize backlog, analyze stories, analyze traceability, produce reports. | `tests/`, `README.md` |
| Zahtevi za eksternim resursima | Jira Cloud, GitHub repository, OpenAI API, optional Ollama later. | `.env.example`, `requirements.txt` |
| Nefunkcionalni zahtevi | No secrets in repo, repeatable offline demo, structured output, deterministic tests. | `.gitignore`, tests, fixtures |
| Dodaci | Timeline, team roles, technologies, references. | `docs/jira-backlog.md`, SRS document |

