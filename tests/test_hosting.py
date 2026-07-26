import pytest

from app.hosting import latest_deployment, list_deployments

# What Vercel serves today. The fake below answers ONLY this path, so a call to a retired
# endpoint fails the way it does in production: a 404, not a silent wrong answer.
CURRENT_PATH = "/v13/deployments"


class FakeVercel:
    def __init__(self, deployments=None):
        self.deployments = [{"uid": "dpl_1", "state": "READY"}] if deployments is None else deployments
        self.calls = []

    def get(self, path, params=None):
        self.calls.append((path, params))
        if path != CURRENT_PATH:
            raise LookupError(f"404 unknown endpoint: {path}")
        return {"deployments": self.deployments, "pagination": {"count": len(self.deployments)}}


def test_list_deployments_calls_the_current_endpoint():
    client = FakeVercel()
    list_deployments(client, "prj_1")
    assert client.calls[0][0] == CURRENT_PATH


def test_list_deployments_returns_the_deployments():
    client = FakeVercel([{"uid": "dpl_a", "state": "READY"}, {"uid": "dpl_b", "state": "ERROR"}])
    assert [d["uid"] for d in list_deployments(client, "prj_1")] == ["dpl_a", "dpl_b"]


def test_latest_deployment_returns_newest():
    client = FakeVercel([{"uid": "dpl_new", "state": "READY"}])
    assert latest_deployment(client, "prj_1")["uid"] == "dpl_new"


def test_latest_deployment_is_none_when_never_shipped():
    assert latest_deployment(FakeVercel([]), "prj_1") is None


def test_project_id_is_required():
    with pytest.raises(ValueError):
        list_deployments(FakeVercel(), "")
