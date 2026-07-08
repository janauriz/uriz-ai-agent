import unittest
from pathlib import Path

from src.uriz_agent.agent.graph import run_audit
from src.uriz_agent.reporting import write_report_bundle


FIXTURES = Path(__file__).parent / "fixtures"


class AuditWorkflowTests(unittest.TestCase):
    def test_run_audit_offline(self) -> None:
        report = run_audit(
            jira_file=FIXTURES / "jira_export.json",
            github_dir=Path("."),
            github_pr_file=FIXTURES / "pull_requests.json",
            project_key="URIZ",
            use_llm=False,
            run_id="test-run",
        )
        self.assertEqual(report.issues_analyzed, 4)
        self.assertLess(report.story_quality_score, 100)
        self.assertTrue(any(item.issue_key == "URIZ-2" for item in report.missing_acceptance_criteria))
        self.assertTrue(any(item.issue_key == "URIZ-4" for item in report.github_linkage_gaps))
        self.assertFalse(any(item.issue_key == "URIZ-3" for item in report.github_linkage_gaps))

    def test_write_report_bundle(self) -> None:
        report = run_audit(
            jira_file=FIXTURES / "jira_export.json",
            github_dir=Path("."),
            github_pr_file=FIXTURES / "pull_requests.json",
            project_key="URIZ",
            use_llm=False,
            run_id="test-report",
        )
        outputs = write_report_bundle(report, Path("reports") / "unit-test")
        self.assertTrue(outputs["json"].exists())
        self.assertTrue(outputs["markdown"].exists())
        self.assertIn("Traceability", outputs["markdown"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()



