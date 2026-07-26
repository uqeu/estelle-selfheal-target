import pytest

from app.mailer import send_email


class FakeResend:
    def __init__(self):
        self.calls = []

    def post(self, path, json=None):
        self.calls.append((path, json))
        return {"id": "msg_123"}


def test_send_email_returns_the_message_id():
    assert send_email(FakeResend(), "a@example.dev", "Hi", "<p>Hi</p>") == "msg_123"


def test_send_email_wraps_a_single_recipient_in_a_list():
    client = FakeResend()
    send_email(client, "a@example.dev", "Hi", "<p>Hi</p>")
    assert client.calls[0][1]["to"] == ["a@example.dev"]


def test_send_email_keeps_multiple_recipients():
    client = FakeResend()
    send_email(client, ["a@example.dev", "b@example.dev"], "Hi", "<p>Hi</p>")
    assert client.calls[0][1]["to"] == ["a@example.dev", "b@example.dev"]


def test_send_email_requires_a_recipient():
    with pytest.raises(ValueError):
        send_email(FakeResend(), "", "Hi", "<p>Hi</p>")
