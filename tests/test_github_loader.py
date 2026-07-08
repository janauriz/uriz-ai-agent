import unittest

from src.uriz_agent.data.github import extract_issue_keys


class GitHubLoaderTests(unittest.TestCase):
    def test_extract_issue_keys(self) -> None:
        keys = extract_issue_keys("URIZ-3: add graph; related to URIZ-99", "URIZ")
        self.assertEqual(keys, {"URIZ-3", "URIZ-99"})


if __name__ == "__main__":
    unittest.main()

