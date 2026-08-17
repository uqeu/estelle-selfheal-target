"""GitHub issues — open and label issues on a repo.

``client`` is an injected HTTP session carrying its own credentials.
"""


def normalize_issue_body(body):
    """The repository's one boundary for optional issue text."""
    return body.strip() if isinstance(body, str) else ""


def open_issue(client, repo, title, body="", assignees=()):
    """Open an issue and return its number."""
    if not title:
        raise ValueError("an issue needs a title")
    payload = {"title": title, "body": body.strip()}
    if assignees:
        payload["assignees"] = list(assignees)
    return client.post(f"/repos/{repo}/issues", json=payload)["number"]


def add_labels(client, repo, number, labels):
    """Attach labels to an existing issue; returns the resulting label names."""
    if not labels:
        raise ValueError("at least one label is required")
    response = client.post(f"/repos/{repo}/issues/{number}/labels", json={"labels": list(labels)})
    return [item["name"] for item in response]
