# Traceability Matrix

| Requirement | Jira Epic/Story | Implementation | Test Evidence |
| --- | --- | --- | --- |
| Define concrete AI agent problem | URIZ-9 / URIZ-15 | `README.md`, SRS | Documentation review |
| Use Python, LangChain/LangGraph, LLM | URIZ-6 / URIZ-12 | `src/uriz_agent/agent/graph.py`, `requirements.txt` | `python main.py doctor` |
| Modular project structure | URIZ-4 / URIZ-10 | `main.py`, `src/uriz_agent/` | `python -m unittest discover -s tests` |
| External Jira/GitHub data | URIZ-5 / URIZ-11 | `src/uriz_agent/data/jira.py`, `src/uriz_agent/data/github.py` | Loader tests and fixtures |
| Prompt engineering | URIZ-6 / URIZ-12 | `src/uriz_agent/agent/prompts.py` | Agent report tests |
| User input through CLI/files | URIZ-7 / URIZ-14 | `main.py` | CLI smoke test |
| Structured JSON/Markdown output | URIZ-7 / URIZ-14 | `src/uriz_agent/reporting.py`, `src/uriz_agent/schemas.py` | Report tests |
| README and requirements | URIZ-4 / URIZ-10 | `README.md`, `requirements.txt` | Repo review |
| `.env` for secrets | URIZ-4 / URIZ-10 | `.env.example`, `.gitignore` | Secret scan/manual review |
| Multiple providers/models | URIZ-6 / URIZ-12 | Configurable OpenAI model; Ollama planned | `OPENAI_MODEL` documented |
| Advanced preprocessing | URIZ-6 / URIZ-12 | Normalization, scoring, risk/test heuristics | Unit tests |
| Error handling | URIZ-5 / URIZ-11 | Jira REST diagnostics and CLI error handling | `python main.py jira-check` |
| Three example input classes | URIZ-8 | `tests/fixtures/jira_export.json` | Offline audit report |
| Jira/GitHub linking | URIZ-6 / URIZ-13 | Hook, branch/commit/PR rules, traceability analysis | Validator and workflow tests |
| AI-assisted development disclosure | URIZ-9 / URIZ-15 | SRS chapter 9 documents Codex usage and the original planning prompt | SRS review |
