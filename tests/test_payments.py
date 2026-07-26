import pytest

from app.payments import attach_card, take_payment


class FakeStripe:
    """Stripe as it behaves for a new integration today: cards are PaymentMethods attached to a customer,
    and money moves through a PaymentIntent. The Sources and Charges endpoints are not served."""

    def __init__(self):
        self.calls = []

    def post(self, path, data=None):
        self.calls.append((path, data))
        if "/sources" in path:
            raise LookupError("the Sources API is not available; attach a PaymentMethod instead")
        if path == "/v1/charges":
            raise LookupError("the Charges API is superseded by PaymentIntents")
        if path.endswith("/attach"):
            return {"id": "pm_123", "object": "payment_method"}
        if path == "/v1/payment_intents":
            return {"id": "pi_123", "status": "succeeded"}
        raise LookupError(f"unknown endpoint {path}")


def test_attach_card_attaches_a_payment_method():
    client = FakeStripe()
    attach_card(client, "cus_1", "pm_1")
    assert client.calls[0][0].endswith("/attach")


def test_attach_card_requires_both_ids():
    with pytest.raises(ValueError):
        attach_card(FakeStripe(), "cus_1", "")


def test_take_payment_creates_a_payment_intent():
    client = FakeStripe()
    assert take_payment(client, "cus_1", "pm_1", 500) == "pi_123"
    assert client.calls[0][0] == "/v1/payment_intents"


def test_take_payment_rejects_a_non_positive_amount():
    with pytest.raises(ValueError):
        take_payment(FakeStripe(), "cus_1", "pm_1", 0)
