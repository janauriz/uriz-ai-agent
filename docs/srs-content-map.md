# SRS Content Map

This map keeps `Template 2026.docx`, Jira, the detailed SRS document, and the repository aligned.

| SRS Section | Content For This Project | Repo Evidence |
| --- | --- | --- |
| Introduction | URIZ Backlog QA & Traceability Agent overview, problem context, goals, users, scope, glossary, and references. | `README.md`, `docs/jira-backlog.md`, `docs/URIZ_Backlog_QA_Projektni_zadatak.docx` |
| Aim and purpose | Automate PM/PO checks for story quality, risks, test ideas, and Jira/GitHub traceability. | `README.md`, `src/uriz_agent/agent/graph.py` |
| Users | Product owner, project manager, QA engineer, developer/team member, mentor/assistant. | `docs/traceability-matrix.md`, SRS user table |
| Project scope | CLI MVP with Jira export/REST, local Git scan, structured reports, sample fixtures, and optional OpenAI recommendations. | `main.py`, `src/uriz_agent/`, SRS scope section |
| Globalni opis resenja | Data loaders, schemas, LangGraph workflow, deterministic fallback, LLM analysis, report writer, and deployment models. | `src/uriz_agent/agent/graph.py`, `src/uriz_agent/schemas.py` |
| Opis funkcionalnosti | Detailed FR-01..FR-14 functional requirements mapped to Jira stories. | `tests/`, `README.md`, `docs/traceability-matrix.md` |
| Zahtevi za eksternim resursima | Jira Cloud, GitHub/local Git, OpenAI API, file system, optional Ollama provider, and .env configuration. | `.env.example`, `requirements.txt`, `src/uriz_agent/data/jira.py` |
| Nefunkcionalni zahtevi | Security, repeatability, reliability, traceability, maintainability, structured output, usability, portability, and extensibility. | `.gitignore`, tests, fixtures, Pydantic schemas |
| Test plan i evaluacija | Unit tests, integration tests, offline smoke audit, live Jira check, and current verification results. | `tests/`, `reports/`, `python -m unittest discover -s tests` |
| Korišćenje AI asistenta | Disclosure of Codex usage, original planning prompt, human oversight, verification, and Jira mapping of AI-assisted work. | SRS chapter 9, `AGENTS.md`, implementation history |
| Dodaci | Timeline, team roles, technologies, risk register, future work, conclusion, and references. | `docs/jira-backlog.md`, SRS appendices |
