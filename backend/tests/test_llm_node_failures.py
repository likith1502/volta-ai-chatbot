"""LLMNode must never fail silently: retry once, then show an honest message."""

import pytest

import app.workflow.nodes.llm_node as llm_mod
from app.ai.exceptions import ModelUnavailableException, RateLimitException
from app.ai.models import AIResponse
from app.context.state import ConversationState
from app.workflow.nodes.llm_node import AI_BUSY_MESSAGE, AI_UNAVAILABLE_MESSAGE, LLMNode


class FlakyProvider:
    def __init__(self, errors, reply="Namaste!"):
        self.errors = list(errors)
        self.reply = reply
        self.calls = 0

    async def generate_response(self, request):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return AIResponse(content=self.reply, model_used="fake")


def _state():
    st = ConversationState()
    return st.with_update(current_message={"role": "user", "content": "hi"})


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    async def _instant(_s):
        return None

    monkeypatch.setattr(llm_mod.asyncio, "sleep", _instant)


async def _run(provider):
    node = LLMNode(node_id="llm", provider=provider)
    out = await node.execute(_state())
    return out.execution.node_results["llm"]


@pytest.mark.asyncio
async def test_retries_once_after_rate_limit_then_succeeds():
    p = FlakyProvider([RateLimitException("429")])
    res = await _run(p)
    assert res["content"] == "Namaste!" and p.calls == 2


@pytest.mark.asyncio
async def test_persistent_rate_limit_shows_busy_message():
    p = FlakyProvider([RateLimitException("429"), RateLimitException("429")])
    res = await _run(p)
    assert res["content"] == AI_BUSY_MESSAGE and res["error"] == "RateLimitException"


@pytest.mark.asyncio
async def test_timeout_retried_then_unavailable_message():
    p = FlakyProvider([ModelUnavailableException("t"), ModelUnavailableException("t")])
    res = await _run(p)
    assert res["content"] == AI_UNAVAILABLE_MESSAGE and p.calls == 2


@pytest.mark.asyncio
async def test_unexpected_error_not_retried_and_not_leaked():
    p = FlakyProvider([RuntimeError("secret internal detail")])
    res = await _run(p)
    assert res["content"] == AI_UNAVAILABLE_MESSAGE and p.calls == 1
    assert "secret" not in res["content"]
