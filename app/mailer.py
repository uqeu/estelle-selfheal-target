"""Transactional email via Resend.

``client`` is an injected HTTP session carrying its own credentials.
"""

SEND_PATH = "/emails"


def send_email(client, to, subject, html, sender="noreply@example.dev"):
    """Send one transactional email; returns the provider's message id."""
    if not to:
        raise ValueError("at least one recipient is required")
    recipients = [to] if isinstance(to, str) else list(to)
    response = client.post(SEND_PATH, json={"from": sender, "to": recipients,
                                            "subject": subject, "html": html})
    return response["id"]
