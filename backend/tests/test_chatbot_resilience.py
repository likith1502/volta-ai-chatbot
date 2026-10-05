"""Regression tests for the chatbot failures seen in the customer UI.

- "dont book me a cab" was treated as a booking request
- an overloaded / truncated Gemini reply ended as "couldn't reach the VOLTA assistant"
- the model mixed up an earlier, cancelled trip with the new one
- two quick checkpoints could share a timestamp, restoring stale state
"""

import json

import httpx
import pytest
from app.ai.exceptions import ModelUnavailableException, RateLimitException
from app.ai.models import AIMessage, AIRequest
from app.ai.prompts.recommendation import (
    is_cancellation_intent,
    is_negated_booking,
    is_ride_intent,
)
from app.ai.providers import gemini_provider as gp
from app.checkpoints.checkpoint import Checkpoint
from app.context.state import ConversationState

from tests.test_natural_booking_flow import GEMINI_QUOTE, GeminiLikeProvider, _setup

# ------------------------------------------------------------ negations


@pytest.mark.parametrize(
    "text",
    [
        "dont book me a cab",
        "don't book me a cab",
        "Do not book a ride",
        "I don't want a cab",
        "no need for a taxi",
        "never book a car for me",
    ],
)
def test_declining_a_ride_is_not_a_booking(text):
    assert is_negated_booking(text)
    assert is_cancellation_intent(text)
    assert not is_ride_intent(text)


@pytest.mark.parametrize(
    "text",
    [
        "book me a cab",
        "book me a ride from marredpally to hitechcity",
        "don't cancel my ride",
        "I don't know how to book a cab",
        "don't worry, book me a cab to Madhapur",
    ],
)
def test_normal_requests_are_unchanged(text):
    assert not is_negated_booking(text)


def test_dont_cancel_keeps_the_ride():
    assert not is_cancellation_intent("don't cancel my ride")


@pytest.mark.asyncio
async def test_dont_book_a_cab_books_nothing_and_does_not_ask_for_pickup():
    say, booking = _setup()
    turn = await say("dont book me a cab")
    booking.create_booking_from_recommendation.assert_not_awaited()
    assert "won't book" in turn["content"]
    assert "pick" not in turn["content"].lower()


@pytest.mark.asyncio
async def test_new_ride_after_cancel_uses_the_new_route():
    say, _ = _setup()
    await say("Book a cab from Home to Work")
    await say("cancel my ride")
    turn = await say("book me a ride from Work to Home")
    ride = turn["final_state"].memory.extracted_entities["ride"]
    assert ride["pickup_raw"].lower() == "work"
    assert ride["destination_raw"].lower() == "home"
    assert not ride["is_cancelled"]


@pytest.mark.asyncio
async def test_off_topic_message_never_repeats_an_old_ride_step():
    say, _ = _setup()
    await say("Book a cab from Home to Work")
    await say("Sedan")
    declined = await say("no")
    assert "haven't booked anything" in declined["content"]
    later = await say("give me python code")
    assert "haven't booked anything" not in later["content"]
    assert later["content"] == GEMINI_QUOTE  # the assistant's own reply is shown


# ------------------------------------------------------- LLM node context


@pytest.mark.asyncio
async def test_model_is_told_which_trip_is_current(monkeypatch):
    seen: list[AIRequest] = []
    original = GeminiLikeProvider.generate_response

    async def spy(self, request):
        seen.append(request)
        return await original(self, request)

    monkeypatch.setattr(GeminiLikeProvider, "generate_response", spy)
    say, _ = _setup()
    await say("Book a cab from Home to Work")
    sent = "\n".join(m.content for m in seen[-1].messages)
    assert "[Current Ride Request]" in sent
    assert "Destination: Work" in sent


# ------------------------------------------------- AI down: still useful


@pytest.mark.asyncio
async def test_ai_unavailable_still_shows_cars_and_fares(monkeypatch):
    async def boom(self, request):
        raise ModelUnavailableException("overloaded")

    monkeypatch.setattr(GeminiLikeProvider, "generate_response", boom)
    monkeypatch.setattr("app.workflow.nodes.llm_node.RETRY_DELAY_SECONDS", 0)
    say, _ = _setup()
    turn = await say("Book a cab from Home to Work")
    assert "couldn't reach" not in turn["content"]
    assert "Volta Sedan" in turn["content"] and "₹" in turn["content"]
    assert "Which car would you like?" in turn["content"]


# ------------------------------------------------ Gemini provider fallback


_REAL_ASYNC_CLIENT = httpx.AsyncClient


def _patch_http(monkeypatch, handler):
    real = _REAL_ASYNC_CLIENT
    monkeypatch.setattr(
        gp.httpx,
        "AsyncClient",
        lambda **kw: real(**{**kw, "transport": httpx.MockTransport(handler)}),
    )


def _ok(text, finish="stop", model="m"):
    return httpx.Response(
        200,
        json={
            "model": model,
            "choices": [
                {"message": {"role": "assistant", "content": text}, "finish_reason": finish}
            ],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        },
    )


def _provider(monkeypatch, fallbacks="b-model,c-model"):
    monkeypatch.setattr(gp.settings, "GEMINI_FALLBACK_MODELS", fallbacks)
    return gp.GeminiProvider(api_key="k", model="gemini-3.8-flash", max_tokens=1000)


def _req():
    return AIRequest(messages=[AIMessage(role="user", content="hi")], system_prompt="s")


@pytest.mark.asyncio
async def test_overloaded_primary_falls_back_to_next_model(monkeypatch):
    calls = []

    def handler(request):
        model = json.loads(request.content)["model"]
        calls.append(model)
        if model == "gemini-3.8-flash":
            return httpx.Response(503, json={"error": {"message": "high demand"}})
        return _ok("Hello there", model=model)

    _patch_http(monkeypatch, handler)
    resp = await _provider(monkeypatch).generate_response(_req())
    assert resp.content == "Hello there"
    assert calls == ["gemini-3.8-flash", "b-model"]


@pytest.mark.asyncio
async def test_rate_limit_truncated_and_empty_replies_all_fall_back(monkeypatch):
    def handler(request):
        model = json.loads(request.content)["model"]
        if model == "gemini-3.8-flash":
            return httpx.Response(429, json={})
        if model == "b-model":
            return _ok("Assuming you want the ride from **", finish="length")
        if model == "c-model":
            return _ok("   ")
        return _ok("Full answer", model=model)

    _patch_http(monkeypatch, handler)
    resp = await _provider(monkeypatch, "b-model,c-model,d-model").generate_response(_req())
    assert resp.content == "Full answer"


@pytest.mark.asyncio
async def test_all_models_down_raises_for_the_node_to_handle(monkeypatch):
    _patch_http(monkeypatch, lambda r: httpx.Response(503, json={}))
    with pytest.raises(ModelUnavailableException):
        await _provider(monkeypatch).generate_response(_req())
    _patch_http(monkeypatch, lambda r: httpx.Response(429, json={}))
    with pytest.raises(RateLimitException):
        await _provider(monkeypatch).generate_response(_req())


@pytest.mark.asyncio
async def test_thinking_models_get_a_big_budget_and_low_reasoning(monkeypatch):
    sent = {}

    def handler(request):
        sent.update(json.loads(request.content))
        return _ok("ok")

    _patch_http(monkeypatch, handler)
    await _provider(monkeypatch).generate_response(_req())
    assert sent["max_tokens"] >= 4096
    assert sent["reasoning_effort"] == gp.settings.GEMINI_REASONING_EFFORT


# ------------------------------------------------------- checkpoint order


def test_checkpoint_timestamps_strictly_increase():
    state = ConversationState()
    cps = [Checkpoint(workflow_id="w", graph_id="g", state_snapshot=state) for _ in range(200)]
    stamps = [c.timestamp for c in cps]
    assert all(a < b for a, b in zip(stamps, stamps[1:]))
    assert max(cps, key=lambda c: c.timestamp) is cps[-1]
