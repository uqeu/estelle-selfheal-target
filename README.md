# estelle-selfheal-target

A throwaway application that plays **the customer** in Estelle's self-heal simulation.

It is a small, ordinary Python service that talks to four vendors through injected HTTP clients:

| Module | Vendor | What it does |
| --- | --- | --- |
| `app/hosting.py` | Vercel | list a project's deployments |
| `app/mailer.py` | Resend | send transactional email |
| `app/issues.py` | GitHub | open and label issues |
| `app/payments.py` | Stripe | attach a card, take a payment |

## The point

One module at a time is left calling a **genuinely retired vendor API**. Its tests assert the API
that vendor serves *today*, so the suite is honestly **red** at baseline — nothing is mocked into
failing. Estelle then has to notice the drift, research the current API live, fix the call, prove
the fix in a sandbox, and open or merge a PR.

The suite must be **fully green after the fix**, which is why only one vendor is stale per run:
the repro-sandbox rejects any fix that leaves another test failing.

## Running the tests

```bash
python -m pytest -q
```

This repo is disposable. Nothing here is production code and no credentials live in it — every
module takes an already-authenticated `client` as an argument.
