"""Card payments via Stripe, built on the Sources API.

``client`` is an injected Stripe-shaped session carrying its own credentials.
"""


def attach_card(client, customer_id, source_token):
    """Attach a saved card to a customer so it can be charged later."""
    if not (customer_id and source_token):
        raise ValueError("customer_id and source_token are required")
    client.post(f"/v1/customers/{customer_id}/sources", data={"source": source_token})
    return source_token


def take_payment(client, customer_id, source_token, amount_cents, currency="usd"):
    """Charge a stored card, returning the resulting charge id."""
    if amount_cents <= 0:
        raise ValueError("amount_cents must be positive")
    charge = client.post("/v1/charges", data={
        "customer": customer_id,
        "source": source_token,
        "amount": amount_cents,
        "currency": currency,
    })
    return charge["id"]
