"""Natural-language booking: everyday "yes"/"no" replies and consistent prices.

Covers:
- "yes", "Yes.", "haan", "ok book it", "avunu" confirm a chosen vehicle
- naming a different vehicle switches choice (never books the old one)
- "no" after choosing books nothing
- "yes" before choosing a vehicle asks which car (books nothing)
- the fare Gemini showed is the fare used for selection and booking
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ai.base import AIProvider
from app.ai.models import AIRequest, AIResponse, AITokenUsage
from app.ai.prompts.human_text import (
    extract_quoted_fares,
    format_inr,
    is_affirmative_reply,
    is_negative_reply,
    place_name,
)
from app.ai.tools.booking_tool import BookingTool
from app.ai.tools.dispatcher import AIToolDispatcher
from app.ai.tools.recommendation_tool import RecommendationTool
from app.ai.tools.registry import AIToolRegistry
from app.checkpoints.checkpoint_manager import CheckpointManager
from app.checkpoints.checkpoint_store import InMemoryCheckpointStore
from app.fleet.demo import DemoFleetPricingProvider
from app.models.booking import Booking
from app.models.conversation import Conversation
from app.models.enums import BookingStatus, RecommendationStatus
from app.models.recommendation import Recommendation
from app.models.saved_location import SavedLocation
from app.services.booking import BookingService
from app.services.cab_pricing import CabPricingService
from app.services.chat_graph import ChatGraphOrchestrator

# What the real Gemini replies look like (its own estimates, not demo fares).
GEMINI_QUOTE = (
    "Sure! From **Home** to **Work** is about ~8 km, roughly 25 minutes.\n\n"
    "1. **Volta Mini** – ~₹130\n   Compact car for up to 4\n"
    "2. **Volta Sedan** – ~₹170\n   Comfortable car for up to 4\n"
    "3. **Volta SUV** – ~₹240\n"
    "4. **Volta EV** – ~₹160\n"
    "5. **Volta Luxury** – ~₹350\n\n"
    "Which one would you like?"
)


class GeminiLikeProvider(AIProvider):
    async def generate_response(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content=GEMINI_QUOTE,
            model_used="gemini-test",
            usage=AITokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
            tool_calls=[],
        )


# ---------------------------------------------------------------- unit tests


@pytest.mark.parametrize(
    "text",
    [
        "yes", "Yes.", "YES!", "yeah", "ok", "Okay.", "sure", "book it",
        "yes please book it", "ok go ahead", "haan", "haan ji", "theek hai",
        "kar do", "avunu", "sare", "book cheyyi", "Yes, confirm.", "confirm",
    ],
)
def test_affirmative_replies(text):
    assert is_affirmative_reply(text)


@pytest.mark.parametrize(
    "text",
    ["no", "No.", "nope", "wait", "not now", "don't book", "nahi", "vaddu",
     "yes but change the car", "no, book it later"],
)
def test_not_affirmative(text):
    assert not is_affirmative_reply(text)


@pytest.mark.parametrize("text", ["no", "No.", "nope", "wait", "not now", "nahi", "vaddu"])
def test_negative_replies(text):
    assert is_negative_reply(text)


def test_format_inr_and_place_name():
    assert format_inr("520.00") == "₹520"
    assert format_inr(125000) == "₹1,25,000"
    assert place_name("jubilee hills", "x") == "Jubilee Hills"
    assert place_name("HITEC City", "x") == "HITEC City"
    assert place_name(None, "your pickup") == "your pickup"


def test_extract_quoted_fares_from_gemini_text():
    options = [{"tier": t, "display_name": n} for t, n in
               [("mini", "Mini"), ("sedan", "Sedan"), ("suv", "SUV"), ("ev", "EV"), ("luxury", "Luxury")]]
    fares = extract_quoted_fares(GEMINI_QUOTE, options)
    assert fares == {"mini": "130.00", "sedan": "170.00", "suv": "240.00", "ev": "160.00", "luxury": "350.00"}


def test_extract_quoted_fares_other_formats():
    options = [{"tier": "sedan", "display_name": "Sedan"}, {"tier": "suv", "display_name": "SUV"}]
    assert extract_quoted_fares("* Sedan: Rs. 1,250\n* SUV: INR 1800", options) == {
        "sedan": "1250.00", "suv": "1800.00",
    }
    # Unclear text -> nothing changed (stored quote is kept)
    assert extract_quoted_fares("We have sedans and SUVs.", options) == {}


# ---------------------------------------------------------------- flow tests


def _setup():
    user_id, conv_id = uuid.uuid4(), uuid.uuid4()
    home = SavedLocation(id=uuid.uuid4(), user_id=user_id, label="Home",
                         address="Indiranagar", latitude=12.97, longitude=77.59)
    work = SavedLocation(id=uuid.uuid4(), user_id=user_id, label="Work",
                         address="Whitefield", latitude=12.96, longitude=77.75)
    session = AsyncMock()
    session.add = MagicMock()
    pricing = CabPricingService(session=session, provider=DemoFleetPricingProvider())
    rec_id = uuid.uuid4()
    rec = Recommendation(id=rec_id, conversation_id=conv_id, recommendation_type="cab_availability",
                         status=RecommendationStatus.PENDING, recommendation_data={})
    pricing.recommendation_service.create_recommendation = AsyncMock(return_value=rec)
    booking_service = BookingService(session)
    booking_service.create_booking_from_recommendation = AsyncMock(
        return_value=Booking(id=uuid.uuid4(), recommendation_id=rec_id, booking_reference="BK-NATURAL1",
                             booking_status=BookingStatus.CONFIRMED, provider="volta_fleet",
                             booked_at=datetime.now(timezone.utc))
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id))
    registry = AIToolRegistry()
    registry.register(RecommendationTool(session=session, cab_pricing_service=pricing))
    registry.register(BookingTool(session=session, booking_service=booking_service))
    orch = ChatGraphOrchestrator(
        provider=GeminiLikeProvider(),
        tool_dispatcher=AIToolDispatcher(registry),
        checkpoint_manager=CheckpointManager(store=InMemoryCheckpointStore()),
    )

    async def say(text):
        return await orch.execute_chat_turn(
            conversation_id=conv_id, user_id=user_id, session_id="s",
            message_text=text, saved_locations=[home, work])

    return say, booking_service


@pytest.mark.asyncio
async def test_gemini_fares_are_stored_and_used_for_selection():
    say, _ = _setup()
    t1 = await say("Book a cab from Home to Work")
    assert t1["fare_overrides"]["sedan"] == "170.00"
    ride = t1["final_state"].memory.extracted_entities["ride"]
    sedan = next(o for o in ride["available_options"] if o["tier"] == "sedan")
    assert sedan["fare"] == "170.00"  # Gemini's price, not the demo ₹240

    t2 = await say("Sedan")
    assert "₹170" in t2["content"] and "₹240" not in t2["content"]
    assert "Shall I book it for you?" in t2["content"]
    assert "Please reply" not in t2["content"] and "INR" not in t2["content"]


@pytest.mark.asyncio
@pytest.mark.parametrize("reply", ["yes", "Yes.", "haan", "ok book it", "avunu", "sure"])
async def test_everyday_yes_confirms_chosen_vehicle(reply):
    say, booking = _setup()
    await say("Book a cab from Home to Work")
    await say("Sedan")
    t3 = await say(reply)
    booking.create_booking_from_recommendation.assert_awaited_once()
    assert "BK-NATURAL1" in t3["content"] and "is booked" in t3["content"]
    assert "₹170" in t3["content"]  # same price the customer saw


@pytest.mark.asyncio
async def test_naming_a_different_vehicle_switches_instead_of_booking():
    say, booking = _setup()
    await say("Book a cab from Home to Work")
    await say("Sedan")
    t3 = await say("book the SUV")
    booking.create_booking_from_recommendation.assert_not_awaited()
    assert "Volta SUV" in t3["content"] and "Shall I book it for you?" in t3["content"]
    t4 = await say("yes")
    booking.create_booking_from_recommendation.assert_awaited_once()
    assert "Your Volta SUV is booked." in t4["content"]


@pytest.mark.asyncio
async def test_no_after_choosing_books_nothing():
    say, booking = _setup()
    await say("Book a cab from Home to Work")
    await say("Sedan")
    t3 = await say("no")
    booking.create_booking_from_recommendation.assert_not_awaited()
    assert "haven't booked anything" in t3["content"]
    # and a later plain "yes" must not book the cleared choice
    t4 = await say("yes")
    booking.create_booking_from_recommendation.assert_not_awaited()
    assert "Which car would you like?" in t4["content"]


@pytest.mark.asyncio
async def test_yes_before_choosing_asks_which_car():
    say, booking = _setup()
    await say("Book a cab from Home to Work")
    t2 = await say("yes")
    booking.create_booking_from_recommendation.assert_not_awaited()
    assert "Which car would you like?" in t2["content"]


@pytest.mark.asyncio
async def test_chat_service_saves_gemini_fares_into_stored_quote():
    """The booking reads its fare from the stored quote, so it must be updated."""
    from app.services.chat import ChatService

    rec_id = uuid.uuid4()
    rec = Recommendation(
        id=rec_id, conversation_id=uuid.uuid4(), recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={"options": [
            {"tier": "sedan", "display_name": "Sedan", "fare": "240.00"},
            {"tier": "suv", "display_name": "SUV", "fare": "360.00"},
        ], "currency": "INR"},
    )
    session = AsyncMock()
    session.get = AsyncMock(return_value=rec)
    service = ChatService.__new__(ChatService)  # only the helper is under test
    service.session = session

    await service._apply_quoted_fares({"fare_overrides": {"sedan": "170.00"}}, rec_id)

    opts = {o["tier"]: o["fare"] for o in rec.recommendation_data["options"]}
    assert opts == {"sedan": "170.00", "suv": "360.00"}  # SUV had no Gemini price: kept
    assert rec.recommendation_data["fare_source"] == "assistant_estimate"
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_chat_service_fare_save_failure_never_breaks_reply():
    from app.services.chat import ChatService

    session = AsyncMock()
    session.get = AsyncMock(side_effect=RuntimeError("db down"))
    service = ChatService.__new__(ChatService)
    service.session = session
    # must not raise
    await service._apply_quoted_fares({"fare_overrides": {"sedan": "170.00"}}, uuid.uuid4())
