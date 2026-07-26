def assess(prompt):
    """The BYOK model judging which of OUR APIs actually changed, grounded on the cited excerpts."""
    body = {"model": os.environ.get("ESTELLE_SIM_ASSESS_MODEL", "openai/gpt-5.5"),
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
                 "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]


# --- the run -----------------------------------------------------------------------------------------------

def _load_config():
    """Load exactly what this run needs, the same way the server does (``os.environ.setdefault``, so an
    already-exported value always wins). Keeps secrets out of the invoking shell: the Firecrawl + OpenRouter
    keys are read from .env here and never exported around them."""
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    env_path = os.path.join(root, ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    name, value = line.split("=", 1)
                    os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))
    state = os.path.expanduser("~/.estelle-dogfood/local-webhook-secret")
    defaults = {
        "GITHUB_APP_ID": "4319081",
        "GITHUB_APP_SLUG": "estelle-fatelabs",
        "GITHUB_APP_PRIVATE_KEY_PATH": os.path.expanduser(
            "~/Downloads/estelle-fatelabs.2026-07-16.private-key.pem"),
        "ESTELLE_AUTOREPAIR_REPO": os.path.expanduser("~/estelle-selfheal-target"),
    }
    if os.path.exists(state):
        with open(state) as fh:
            defaults["GITHUB_APP_WEBHOOK_SECRET"] = fh.read().strip()
    for name, value in defaults.items():
        os.environ.setdefault(name, value)


_load_config()

BASE = os.environ.get("ESTELLE_SIM_BASE", "http://127.0.0.1:8787")
REPO = os.path.expanduser(os.environ.get("ESTELLE_AUTOREPAIR_REPO", "~/estelle-selfheal-target"))
REPO_SLUG = os.environ.get("ESTELLE_SIM_REPO_SLUG", "uqeu/estelle-selfheal-target")
INSTALLATION_ID = int(os.environ.get("ESTELLE_SIM_INSTALLATION_ID", "147117265"))
ACCOUNTS = os.path.expanduser("~/.estelle-dogfood/accounts.json")

# The vendors this sim knows how to break, and the retired API each module still calls.
VENDORS = {
    # The Chat Completions ``functions`` parameter, deprecated by OpenAI in favour of ``tools``. Real,
    # current, and documented in OpenAI's own changelog — which is the point: the fix has to come from
    # their docs, so the drift has to be one their docs actually describe.
    "openai": Vendor(name="openai", apis=("functions",)),
    "github": Vendor(name="github", apis=("assignee",)),
    "stripe": Vendor(name="stripe", apis=("Source",)),
    "vercel": Vendor(name="vercel", apis=("/v5/now/deployments",)),
    "resend": Vendor(name="resend", apis=("/emails",)),
}

"""Run the self-heal simulation end to end and print the whole trail.

    vendor drift  →  live research  →  grounded fix  →  merge gate  →  repro-sandbox  →  auto-merge

Every leg is the SHIPPED module doing its real job — :mod:`~estelle.serve.vendor_drift` finds the drift,
Firecrawl does the research, ``POST /work`` drafts through the deterministic merge gate,
:mod:`~estelle.serve.repro_sandbox` reproduces the failure and verifies the fix against the repo's own suite,
:func:`~estelle.serve.auto_mode.decide_auto_merge` rules on the merge, and the GitHub App performs it. The new
piece is :mod:`~estelle.serve.drift_repair`, which joins them and enforces the one rule none of them can:
**a vendor fix is written from the vendor's live docs, never from model memory.**

This is a harness, not a product endpoint. It orchestrates the same modules ``/autorepair`` does, because
``/autorepair`` builds its own fixed defensive-guard