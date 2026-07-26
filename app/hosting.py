"""Vercel deployments — a thin wrapper over their REST API.

``client`` is an injected HTTP session (it carries its own credentials), so this module stays
testable without a network and holds no secrets of its own.
"""

# The deployments endpoint we call.
DEPLOYMENTS_PATH = "/v13/deployments"


def list_deployments(client, project_id, limit=10):
    """Recent deployments for a project, newest first."""
    if not project_id:
        raise ValueError("project_id is required")
    payload = client.get(DEPLOYMENTS_PATH, params={"projectId": project_id, "limit": limit})
    return payload["deployments"]


def latest_deployment(client, project_id):
    """The most recent deployment, or None when the project has never shipped."""
    items = list_deployments(client, project_id, limit=1)
    return items[0] if items else None
