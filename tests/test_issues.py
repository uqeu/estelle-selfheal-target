import pytest

from app.issues import add_labels, open_issue


class FakeGitHub:
    def __init__(self):
        self.calls = []

    def post(self, path, json=None):
        self.calls.append((path, json))
        if path.endswith("/labels"):
            return [{"name": name} for name in json["labels"]]
        return {"number": 42}


def test_open_issue_returns_the_number():
    assert open_issue(FakeGitHub(), "acme/site", "It broke") == 42


def test_open_issue_sends_assignees_as_a_list():
    client = FakeGitHub()
    open_issue(client, "acme/site", "It broke", assignees=["rivera"])
    assert client.calls[0][1]["assignees"] == ["rivera"]


def test_open_issue_omits_assignees_when_none_given():
    client = FakeGitHub()
    open_issue(client, "acme/site", "It broke")
    assert "assignees" not in client.calls[0][1]


def test_open_issue_requires_a_title():
    with pytest.raises(ValueError):
        open_issue(FakeGitHub(), "acme/site", "")


def test_add_labels_returns_the_names():
    assert add_labels(FakeGitHub(), "acme/site", 42, ["bug"]) == ["bug"]


def test_add_labels_requires_at_least_one():
    with pytest.raises(ValueError):
        add_labels(FakeGitHub(), "acme/site", 42, [])
