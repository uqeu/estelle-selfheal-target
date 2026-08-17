"""Shared text normalization boundaries."""


def normalize_issue_body(body):
    """Return optional issue text in the wire format the GitHub client expects."""
    return body.strip() if isinstance(body, str) else ""
