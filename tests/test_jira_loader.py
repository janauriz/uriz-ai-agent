import unittest
from pathlib import Path

from src.uriz_agent.data.jira import load_jira_issues


FIXTURE = Path(__file__).parent / "fixtures" / "jira_export.json"


class JiraLoaderTests(unittest.TestCase):
    def test_loads_jira_export(self) -> None:
        issues = load_jira_issues(FIXTURE)
        self.assertEqual(len(issues), 12)
        self.assertEqual(issues[0].key, "URIZ-4")
        story = next(issue for issue in issues if issue.key == "URIZ-12")
        self.assertEqual(story.parent_key, "URIZ-6")
        self.assertEqual(
            story.acceptance_criteria[0],
            "Given a Jira story with no acceptance criteria, when audit runs, then the report flags it.",
        )
        epic_keys = {issue.key for issue in issues if issue.issue_type == "Epic"}
        story_keys = {issue.key for issue in issues if issue.issue_type == "Story"}
        self.assertEqual(epic_keys, {"URIZ-4", "URIZ-5", "URIZ-6", "URIZ-7", "URIZ-8", "URIZ-9"})
        self.assertEqual(story_keys, {"URIZ-10", "URIZ-11", "URIZ-12", "URIZ-13", "URIZ-14", "URIZ-15"})


if __name__ == "__main__":
    unittest.main()
