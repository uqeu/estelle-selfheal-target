"""Ask an OpenAI chat model a question, with one callable tool available.

``client`` is an injected chat-completions session carrying its own credentials.
"""

WEATHER_TOOL = {
    "name": "get_weather",
    "description": "Look up the current weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name"}},
        "required": ["city"],
    },
}


def ask(client, prompt, model="gpt-4o-mini"):
    """Send one prompt with the weather tool available; returns the assistant's message."""
    if not prompt:
        raise ValueError("prompt is required")
    response = client.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        functions=[WEATHER_TOOL],
    )
    return response["choices"][0]["message"]