import unittest

from src.uriz_agent.data.github import extract_issue_keys


class GitHubLoaderTests(unittest.TestCase):
    def test_extract_issue_keys(self) -> None:
        keys = extract_issue_keys("URIZ-13: add traceability; related to URIZ-99", "URIZ")
        self.assertEqual(keys, {"URIZ-13", "URIZ-99"})


if __name__ == "__main__":
    unittest.main()

