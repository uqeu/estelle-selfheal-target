import pytest

from app.assistant import ask


class FakeOpenAI:
    """Stands in for the chat-completions endpoint as it behaves today: the retired `functions` parameter is
    rejected outright, and a tool-calling request must use `tools`."""

    def __init__(self):
        self.last = None

    def create(self, **kwargs):
        self.last = kwargs
        if "functions" in kwargs:
            raise TypeError("the 'functions' parameter is no longer accepted; use 'tools'")
        if "function_call" in kwargs:
            raise TypeError("the 'function_call' parameter is no longer accepted; use 'tool_choice'")
        if "tools" not in kwargs:
            raise TypeError("a tool-calling request must pass 'tools'")
        return {"choices": [{"message": {"role": "assistant", "content": "It is 20C."}}]}


def test_ask_sends_tools_not_functions():
    client = FakeOpenAI()
    ask(client, "weather in Toronto")
    assert "functions" not in client.last
    assert client.last["tools"][0]["type"] == "function"


def test_ask_keeps_the_tool_schema():
    client = FakeOpenAI()
    ask(client, "weather in Toronto")
    fn = client.last["tools"][0]["function"]
    assert fn["name"] == "get_weather"
    assert fn["parameters"]["required"] == ["city"]


def test_ask_returns_the_assistant_message():
    assert ask(FakeOpenAI(), "weather in Toronto")["content"] == "It is 20C."


def test_ask_requires_a_prompt():
    with pytest.raises(ValueError):
        ask(FakeOpenAI(), "")
