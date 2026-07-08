from scripts.validate_jira_key import contains_jira_key, main


def test_contains_jira_key() -> None:
    assert contains_jira_key("URIZ-123: add parser")
    assert not contains_jira_key("add parser")


class TestCli:
    def test_main_success(self) -> None:
        assert main(["URIZ-9: demo"]) == 0

    def test_main_failure(self) -> None:
        assert main(["missing key"]) == 1

