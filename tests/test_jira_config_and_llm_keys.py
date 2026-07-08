import os
import unittest
from unittest.mock import patch

from src.uriz_agent.agent.graph import LlmAuditOutput, _filter_llm_output
from src.uriz_agent.data.jira import _jira_jql
from src.uriz_agent.schemas import JiraCommentSuggestion, StoryFinding


class JiraConfigAndLlmKeyTests(unittest.TestCase):
    def test_default_jql_uses_project_field(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(_jira_jql("URIZ"), "project = URIZ ORDER BY created DESC")

    def test_space_jql_is_normalized_to_project_jql(self) -> None:
        with patch.dict(os.environ, {"JIRA_JQL": "space = URIZ ORDER BY created DESC"}, clear=False):
            self.assertEqual(_jira_jql("URIZ"), "project = URIZ ORDER BY created DESC")

    def test_llm_output_filters_unknown_issue_keys(self) -> None:
        output = LlmAuditOutput(
            findings=[
                StoryFinding(issue_key="URIZ-12", severity="medium", category="clarity", message="Valid", recommendation="Keep."),
                StoryFinding(issue_key="URIZ-99", severity="high", category="other", message="Invalid", recommendation="Drop."),
            ],
            jira_comment_suggestions=[
                JiraCommentSuggestion(issue_key="URIZ-12", comment="Valid comment"),
                JiraCommentSuggestion(issue_key="URIZ-99", comment="Invalid comment"),
            ],
        )
        filtered = _filter_llm_output(output, {"URIZ-12"})
        self.assertEqual([item.issue_key for item in filtered.findings], ["URIZ-12"])
        self.assertEqual([item.issue_key for item in filtered.jira_comment_suggestions], ["URIZ-12"])


if __name__ == "__main__":
    unittest.main()
