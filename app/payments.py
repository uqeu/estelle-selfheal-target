"""Card payments via Stripe PaymentMethods and PaymentIntents.

``client`` is an injected Stripe-shaped session carrying its own credentials.
"""


def attach_card(client, customer_id, source_token):
    """Attach a saved card to a customer so it can be charged later."""
    if not (customer_id and source_token):
        raise ValueError("customer_id and source_token are required")
    client.post(f"/v1/payment_methods/{source_token}/attach", data={"customer": customer_id})
    return source_token


def take_payment(client, customer_id, source_token, amount_cents, currency="usd"):
    """Charge a stored card, returning the resulting charge id."""
    if amount_cents <= 0:
        raise ValueError("amount_cents must be positive")
    charge = client.post("/v1/payment_intents", data={
        "customer": customer_id,
        "payment_method": source_token,
        "amount": amount_cents,
        "currency": currency,
        "confirm": True,
    })
    return charge["id"]