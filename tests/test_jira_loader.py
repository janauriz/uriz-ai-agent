import unittest
from pathlib import Path

from src.uriz_agent.data.jira import load_jira_issues


FIXTURE = Path(__file__).parent / "fixtures" / "jira_export.json"


class JiraLoaderTests(unittest.TestCase):
    def test_loads_jira_export(self) -> None:
        issues = load_jira_issues(FIXTURE)
        self.assertEqual(len(issues), 4)
        self.assertEqual(issues[0].key, "URIZ-1")
        self.assertEqual(issues[2].acceptance_criteria[0], "Given a Jira story with no acceptance criteria, when audit runs, then the report flags it.")


if __name__ == "__main__":
    unittest.main()

