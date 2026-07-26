"""Card payments via Stripe.

``client`` is an injected Stripe-shaped session carrying its own credentials.
"""


def attach_card(client, customer_id, payment_method_id):
    """Attach a saved card to a customer so it can be charged later."""
    if not (customer_id and payment_method_id):
        raise ValueError("customer_id and payment_method_id are required")
    client.post(f"/v1/payment_methods/{payment_method_id}/attach", data={"customer": customer_id})
    return payment_method_id


def take_payment(client, customer_id, payment_method_id, amount_cents, currency="usd"):
    """Charge a stored card, returning the resulting intent id."""
    if amount_cents <= 0:
        raise ValueError("amount_cents must be positive")
    intent = client.post("/v1/payment_intents", data={
        "customer": customer_id,
        "payment_method": payment_method_id,
        "amount": amount_cents,
        "currency": currency,
        "confirm": "true",
    })
    return intent["id"]
