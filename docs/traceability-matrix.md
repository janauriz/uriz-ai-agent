# Traceability Matrix

| Requirement | Jira Epic | Implementation | Test Evidence |
| --- | --- | --- | --- |
| Define concrete AI agent problem | URIZ-6 | `README.md`, SRS | Documentation review |
| Use Python, LangChain/LangGraph, LLM | URIZ-3 | `src/uriz_agent/agent/graph.py`, `requirements.txt` | `python main.py doctor` |
| Modular project structure | URIZ-1 | `main.py`, `src/uriz_agent/` | `python -m unittest discover -s tests` |
| External data/service | URIZ-2 | `src/uriz_agent/data/jira.py`, `src/uriz_agent/data/github.py` | Loader tests and fixtures |
| Prompt engineering | URIZ-3 | `src/uriz_agent/agent/prompts.py` | Agent report tests |
| User input through CLI/files | URIZ-4 | `main.py` | CLI smoke test |
| Structured JSON/Markdown output | URIZ-4 | `src/uriz_agent/reporting.py`, `src/uriz_agent/schemas.py` | Report tests |
| README and requirements | URIZ-1 | `README.md`, `requirements.txt` | Repo review |
| `.env` for secrets | URIZ-1 | `.env.example`, `.gitignore` | Secret scan/manual review |
| Multiple providers/models | URIZ-3 | Configurable OpenAI model; Ollama planned | `OPENAI_MODEL` documented |
| Advanced preprocessing | URIZ-3 | Normalization, scoring, risk/test heuristics | Unit tests |
| Error handling | URIZ-4 | CLI validation and report warnings | CLI tests/manual smoke |
| Three example inputs | URIZ-5 | `tests/fixtures/jira_export.json` | Offline audit report |
| Jira/GitHub linking | URIZ-1 | Hook, branch/commit/PR rules | Validator tests |

