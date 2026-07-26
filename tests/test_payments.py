import pytest

from app.payments import attach_card, take_payment


class FakeStripe:
    def __init__(self):
        self.calls = []

    def post(self, path, data=None):
        self.calls.append((path, data))
        return {"id": "pi_123", "status": "succeeded"}


def test_attach_card_posts_to_the_attach_endpoint():
    client = FakeStripe()
    attach_card(client, "cus_1", "pm_1")
    assert client.calls[0][0] == "/v1/payment_methods/pm_1/attach"


def test_attach_card_requires_both_ids():
    with pytest.raises(ValueError):
        attach_card(FakeStripe(), "cus_1", "")


def test_take_payment_returns_the_intent_id():
    assert take_payment(FakeStripe(), "cus_1", "pm_1", 500) == "pi_123"


def test_take_payment_rejects_a_non_positive_amount():
    with pytest.raises(ValueError):
        take_payment(FakeStripe(), "cus_1", "pm_1", 0)
