import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.ai.base import AIProvider
from app.ai.models import AIRequest, AIResponse, AITokenUsage
from app.ai.tools.booking_tool import BookingTool
from app.ai.tools.dispatcher import AIToolDispatcher
from app.ai.tools.recommendation_tool import RecommendationTool
from app.ai.tools.registry import AIToolRegistry
from app.checkpoints.checkpoint_manager import CheckpointManager
from app.checkpoints.checkpoint_store import InMemoryCheckpointStore
from app.exceptions.domain import InvalidBookingStatusException
from app.fleet.demo import DemoFleetPricingProvider
from app.models.booking import Booking
from app.models.conversation import Conversation
from app.models.enums import BookingStatus, RecommendationStatus
from app.models.recommendation import Recommendation
from app.models.saved_location import SavedLocation
from app.schemas.ride import RideEntityState, RideSlotStatus
from app.services.booking import BookingService
from app.services.cab_pricing import CabPricingService
from app.services.chat_graph import ChatGraphOrchestrator


class MockDeterministicAIProvider(AIProvider):
    """Deterministic AI provider mock for graph traversal and intent testing."""

    def __init__(self, response_content: str = "I can assist you with your ride."):
        self.response_content = response_content

    async def generate_response(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content=self.response_content,
            model_used="mock-volta-agent",
            usage=AITokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
            tool_calls=[],
        )


def _create_mock_saved_locations(user_id: uuid.UUID):
    home_id = uuid.uuid4()
    work_id = uuid.uuid4()
    mock_home = SavedLocation(
        id=home_id,
        user_id=user_id,
        label="Home",
        address="100 Palm Grove Road, Indiranagar",
        latitude=12.9716,
        longitude=77.5946,
    )
    mock_work = SavedLocation(
        id=work_id,
        user_id=user_id,
        label="Work",
        address="500 Tech Park, Whitefield",
        latitude=12.9698,
        longitude=77.7500,
    )
    return mock_home, mock_work


class AsyncSessionMock(AsyncMock):
    pass


def _setup_orchestrator(
    session: AsyncSessionMock,
    booking_service: BookingService,
    checkpoint_manager: CheckpointManager,
    rec_tool: Optional[RecommendationTool] = None,
):
    registry = AIToolRegistry()
    if rec_tool:
        registry.register(rec_tool)
    registry.register(BookingTool(session=session, booking_service=booking_service))
    dispatcher = AIToolDispatcher(registry)

    orchestrator = ChatGraphOrchestrator(
        provider=MockDeterministicAIProvider(),
        tool_dispatcher=dispatcher,
        checkpoint_manager=checkpoint_manager,
    )
    return orchestrator, dispatcher



# ============================================================================
# 1. Vehicle Selection: Explicit Options (Mini, Sedan, SUV)
# ============================================================================


@pytest.mark.asyncio
async def test_01_select_each_available_vehicle_tier():
    """Verify selecting Mini, Sedan, or SUV transitions to AWAITING_CONFIRMATION with exact quoted fare."""
    for chosen_tier in ["mini", "sedan", "suv"]:
        user_id = uuid.uuid4()
        conv_id = uuid.uuid4()
        session_id = f"sess_tier_{chosen_tier}"
        mock_home, mock_work = _create_mock_saved_locations(user_id)

        cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
        session = AsyncSessionMock()
        session.add = MagicMock()

        pricing_service = CabPricingService(
            session=session, provider=DemoFleetPricingProvider()
        )
        rec_id = uuid.uuid4()
        mock_rec = Recommendation(
            id=rec_id,
            conversation_id=conv_id,
            recommendation_type="cab_availability",
            status=RecommendationStatus.PENDING,
            recommendation_data={},
        )
        pricing_service.recommendation_service.create_recommendation = AsyncMock(
            return_value=mock_rec
        )
        rec_tool = RecommendationTool(
            session=session, cab_pricing_service=pricing_service
        )
        booking_service = BookingService(session)

        orchestrator, _ = _setup_orchestrator(
            session=session,
            booking_service=booking_service,
            checkpoint_manager=cp_manager,
            rec_tool=rec_tool,
        )

        # Turn 1: Quoting
        t1 = await orchestrator.execute_chat_turn(
            conversation_id=conv_id,
            user_id=user_id,
            session_id=session_id,
            message_text="Book a cab from Home to Work",
            saved_locations=[mock_home, mock_work],
        )
        assert t1["recommendation_id"] is not None

        # Turn 2: User selects tier (e.g. "Sedan" or "I want the sedan")
        t2 = await orchestrator.execute_chat_turn(
            conversation_id=conv_id,
            user_id=user_id,
            session_id=session_id,
            message_text=f"I want the {chosen_tier}",
            saved_locations=[mock_home, mock_work],
        )

        final_ride = RideEntityState.model_validate(
            t2["final_state"].memory.extracted_entities["ride"]
        )
        assert final_ride.status == RideSlotStatus.AWAITING_CONFIRMATION
        assert final_ride.selected_tier == chosen_tier
        assert final_ride.selected_fare is not None
        assert final_ride.is_booked is False
        assert "Would you like to confirm this booking?" in t2["content"]
        assert "tool" not in t2["visited_nodes"]  # Did NOT call BookingService yet!


# ============================================================================
# 2. Rejecting a Tier Not Quoted
# ============================================================================


@pytest.mark.asyncio
async def test_02_reject_tier_not_in_active_quote():
    """Verify requesting an unquoted tier (e.g. Luxury or Auto) does not confirm and prompts for valid tiers."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_reject_tier"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncSessionMock()

    pricing_service = CabPricingService(
        session=session, provider=DemoFleetPricingProvider()
    )
    mock_rec = Recommendation(
        id=uuid.uuid4(),
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        return_value=mock_rec
    )
    rec_tool = RecommendationTool(session=session, cab_pricing_service=pricing_service)
    booking_service = BookingService(session)

    orchestrator, _ = _setup_orchestrator(
        session=session,
        booking_service=booking_service,
        checkpoint_manager=cp_manager,
        rec_tool=rec_tool,
    )

    # Turn 1: Quoting
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )

    # Turn 2: User requests non-existent tier
    t2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book the helicopter",
        saved_locations=[mock_home, mock_work],
    )

    final_ride = RideEntityState.model_validate(
        t2["final_state"].memory.extracted_entities["ride"]
    )
    assert final_ride.is_booked is False
    assert final_ride.selected_tier is None
    assert "not available" in t2["content"] or "choose from" in t2["content"]


# ============================================================================
# 3. Ambiguous "Book it" Asks for Vehicle Tier
# ============================================================================


@pytest.mark.asyncio
async def test_03_ambiguous_booking_asks_which_tier():
    """Verify saying 'Book it' without specifying a tier asks user which quoted option they want."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_ambiguous"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncSessionMock()

    pricing_service = CabPricingService(
        session=session, provider=DemoFleetPricingProvider()
    )
    mock_rec = Recommendation(
        id=uuid.uuid4(),
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        return_value=mock_rec
    )
    rec_tool = RecommendationTool(session=session, cab_pricing_service=pricing_service)
    booking_service = BookingService(session)

    orchestrator, _ = _setup_orchestrator(
        session=session,
        booking_service=booking_service,
        checkpoint_manager=cp_manager,
        rec_tool=rec_tool,
    )

    # Turn 1: Quoting
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )

    # Turn 2: User ambiguously says "Book it"
    t2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book it",
        saved_locations=[mock_home, mock_work],
    )

    final_ride = RideEntityState.model_validate(
        t2["final_state"].memory.extracted_entities["ride"]
    )
    assert final_ride.is_booked is False
    assert final_ride.selected_tier is None
    assert "Which vehicle option would you like to book?" in t2["content"]
    assert "tool" not in t2["visited_nodes"]


# ============================================================================
# 4. Explicit Confirmation Required (Selection Does Not Book)
# ============================================================================


@pytest.mark.asyncio
async def test_04_explicit_confirmation_required_selection_does_not_book():
    """Verify selecting a tier does not create a booking until explicit confirmation is provided."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_explicit_conf"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncSessionMock()
    session.add = MagicMock()

    pricing_service = CabPricingService(
        session=session, provider=DemoFleetPricingProvider()
    )
    rec_id = uuid.uuid4()
    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        return_value=mock_rec
    )
    rec_tool = RecommendationTool(session=session, cab_pricing_service=pricing_service)

    booking_service = BookingService(session)
    booking_service.create_booking_from_recommendation = AsyncMock()

    orchestrator, _ = _setup_orchestrator(
        session=session,
        booking_service=booking_service,
        checkpoint_manager=cp_manager,
        rec_tool=rec_tool,
    )

    # Turn 1: Quoting
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )

    # Turn 2: Select tier -> Must NOT call BookingService
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Sedan",
        saved_locations=[mock_home, mock_work],
    )
    booking_service.create_booking_from_recommendation.assert_not_called()


# ============================================================================
# 5. Full End-to-End Successful Booking
# ============================================================================


@pytest.mark.asyncio
async def test_05_successful_end_to_end_booking():
    """Verify 3-turn flow: (1) Quote -> (2) Select Tier -> (3) Explicit Confirmation -> Confirmed Booking."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_success_bkg"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncSessionMock()
    session.add = MagicMock()

    pricing_service = CabPricingService(
        session=session, provider=DemoFleetPricingProvider()
    )
    rec_id = uuid.uuid4()
    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        return_value=mock_rec
    )
    rec_tool = RecommendationTool(session=session, cab_pricing_service=pricing_service)

    booking_service = BookingService(session)
    booking_id = uuid.uuid4()
    mock_bkg = Booking(
        id=booking_id,
        recommendation_id=rec_id,
        booking_reference="BK-7A8B9C10",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
        booked_at=datetime.now(timezone.utc),
    )
    booking_service.create_booking_from_recommendation = AsyncMock(
        return_value=mock_bkg
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    orchestrator, _ = _setup_orchestrator(
        session=session,
        booking_service=booking_service,
        checkpoint_manager=cp_manager,
        rec_tool=rec_tool,
    )

    # Turn 1: Quoting
    t1 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )
    assert t1["recommendation_id"] is not None

    # Turn 2: Tier Selection
    t2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Volta Sedan",
        saved_locations=[mock_home, mock_work],
    )
    assert "Would you like to confirm this booking?" in t2["content"]

    # Turn 3: Explicit Confirmation
    t3 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Yes, confirm",
        saved_locations=[mock_home, mock_work],
    )

    # Verify Booking Created
    booking_service.create_booking_from_recommendation.assert_awaited_once_with(
        recommendation_id=rec_id,
        provider="volta_fleet",
        external_booking_id=None,
    )

    # Verify Response Content contains confirmed facts only (no invented driver/ETA)
    assert "Your Volta Sedan ride has been successfully booked!" in t3["content"]
    assert "BK-7A8B9C10" in t3["content"]
    assert "Status: Confirmed" in t3["content"]
    assert "Route: Home to Work" in t3["content"]
    assert "driver" not in t3["content"].lower()

    # Traversal verified
    assert t3["visited_nodes"] == [
        "start",
        "intent",
        "decision",
        "llm",
        "tool",
        "memory",
        "response",
        "end",
    ]


# ============================================================================
# 6. Booking Service Failure Handled Honestly
# ============================================================================


@pytest.mark.asyncio
async def test_06_booking_service_failure_reports_not_confirmed():
    """Verify if BookingService fails, chatbot reports booking failure rather than claiming success."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_bkg_failure"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncSessionMock()

    pricing_service = CabPricingService(
        session=session, provider=DemoFleetPricingProvider()
    )
    rec_id = uuid.uuid4()
    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        return_value=mock_rec
    )
    rec_tool = RecommendationTool(session=session, cab_pricing_service=pricing_service)

    booking_service = BookingService(session)
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )
    # Simulate DB/Service error
    booking_service.create_booking_from_recommendation = AsyncMock(
        side_effect=RuntimeError("Database lock failure")
    )

    orchestrator, _ = _setup_orchestrator(
        session=session,
        booking_service=booking_service,
        checkpoint_manager=cp_manager,
        rec_tool=rec_tool,
    )

    # 1. Quote -> 2. Select -> 3. Confirm
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Sedan",
        saved_locations=[mock_home, mock_work],
    )
    t3 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Confirm",
        saved_locations=[mock_home, mock_work],
    )

    assert "unable to confirm your booking" in t3["content"]
    assert "successfully booked" not in t3["content"]


# ============================================================================
# 7. Expired Quote Rejection
# ============================================================================


@pytest.mark.asyncio
async def test_07_expired_quote_rejection():
    """Verify attempting to book an expired recommendation fails and prompts for a fresh quote."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()

    session = AsyncSessionMock()
    booking_service = BookingService(session)

    expired_rec_id = uuid.uuid4()
    expired_rec = Recommendation(
        id=expired_rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.EXPIRED,  # Expired
        recommendation_data={"expires_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()},
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=expired_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    bkg_tool = BookingTool(session=session, booking_service=booking_service)
    result = await bkg_tool.execute(
        {
            "recommendation_id": str(expired_rec_id),
            "conversation_id": str(conv_id),
            "user_id": str(user_id),
            "selected_tier": "sedan",
        }
    )

    assert result.success is False
    assert "expired" in result.error.lower()


# ============================================================================
# 8. User / Conversation Ownership Validation
# ============================================================================


@pytest.mark.asyncio
async def test_08_ownership_validation_prevent_cross_user_booking():
    """Verify User B cannot confirm or book User A's recommendation."""
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    conv_id = uuid.uuid4()

    session = AsyncSessionMock()
    booking_service = BookingService(session)

    rec_id = uuid.uuid4()
    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    # The conversation belongs to User A
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_a)
    )

    bkg_tool = BookingTool(session=session, booking_service=booking_service)
    # User B attempts to book User A's recommendation
    result = await bkg_tool.execute(
        {
            "recommendation_id": str(rec_id),
            "conversation_id": str(conv_id),
            "user_id": str(user_b),
            "selected_tier": "sedan",
        }
    )

    assert result.success is False
    assert "authorization" in result.error.lower() or "permission" in result.error.lower()


# ============================================================================
# 9. Idempotency: Repeated Confirmations Do Not Create Duplicate Bookings
# ============================================================================


@pytest.mark.asyncio
async def test_09_idempotency_repeated_confirmation_returns_existing_booking():
    """Verify replayed or repeated confirmations return existing booking without duplicate row creation."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()

    session = AsyncSessionMock()
    booking_service = BookingService(session)

    rec_id = uuid.uuid4()
    # Recommendation is already ACCEPTED because it was already booked
    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.ACCEPTED,
        recommendation_data={},
    )
    existing_bkg = Booking(
        id=uuid.uuid4(),
        recommendation_id=rec_id,
        booking_reference="BK-EXISTING1",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    # Mock DB query for existing booking
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing_bkg))
    )
    booking_service.create_booking_from_recommendation = AsyncMock()

    bkg_tool = BookingTool(session=session, booking_service=booking_service)
    res = await bkg_tool.execute(
        {
            "recommendation_id": str(rec_id),
            "conversation_id": str(conv_id),
            "user_id": str(user_id),
            "selected_tier": "sedan",
        }
    )

    assert res.success is True
    assert res.data["booking_reference"] == "BK-EXISTING1"
    assert res.data["is_duplicate_replay"] is True
    # create_booking_from_recommendation was NOT called again
    booking_service.create_booking_from_recommendation.assert_not_called()


# ============================================================================
# 10. Knowledge-Base Policy Queries Do Not Trigger Booking
# ============================================================================


@pytest.mark.asyncio
async def test_10_kb_cancellation_policy_does_not_trigger_booking():
    """Verify asking about cancellation policy during active quote does NOT confirm or cancel the booking."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_kb_no_booking"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncSessionMock()

    pricing_service = CabPricingService(
        session=session, provider=DemoFleetPricingProvider()
    )
    rec_id = uuid.uuid4()
    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        return_value=mock_rec
    )
    rec_tool = RecommendationTool(session=session, cab_pricing_service=pricing_service)
    booking_service = BookingService(session)
    booking_service.create_booking_from_recommendation = AsyncMock()

    orchestrator, _ = _setup_orchestrator(
        session=session,
        booking_service=booking_service,
        checkpoint_manager=cp_manager,
        rec_tool=rec_tool,
    )

    # Turn 1: Quoting
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )

    # Turn 2: User asks about cancellation policy
    t2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="What is VOLTA's cancellation policy?",
        saved_locations=[mock_home, mock_work],
    )

    booking_service.create_booking_from_recommendation.assert_not_called()
    assert "tool" not in t2["visited_nodes"]


# ============================================================================
# 11. Reject Confirmation Without Prior Tier Selection
# ============================================================================


@pytest.mark.asyncio
async def test_11_reject_confirmation_without_prior_tier_selection():
    """Verify saying 'Confirm' immediately after quote generation without selecting a tier does NOT book."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_conf_no_tier"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncSessionMock()

    pricing_service = CabPricingService(
        session=session, provider=DemoFleetPricingProvider()
    )
    rec_id = uuid.uuid4()
    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        return_value=mock_rec
    )
    rec_tool = RecommendationTool(session=session, cab_pricing_service=pricing_service)
    booking_service = BookingService(session)
    booking_service.create_booking_from_recommendation = AsyncMock()

    orchestrator, _ = _setup_orchestrator(
        session=session,
        booking_service=booking_service,
        checkpoint_manager=cp_manager,
        rec_tool=rec_tool,
    )

    # Turn 1: Quoting
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )

    # Turn 2: User says "Confirm" directly without picking a tier
    t2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Confirm",
        saved_locations=[mock_home, mock_work],
    )

    booking_service.create_booking_from_recommendation.assert_not_called()
    assert "Which vehicle option would you like to book?" in t2["content"]
    assert "tool" not in t2["visited_nodes"]


# ============================================================================
# 12. Non-Pending Recommendation Status Rejection
# ============================================================================


@pytest.mark.asyncio
async def test_12_non_pending_recommendation_status_rejected():
    """Verify attempting to book a recommendation with status REJECTED fails cleanly."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()

    session = AsyncSessionMock()
    booking_service = BookingService(session)

    rec_id = uuid.uuid4()
    rejected_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.REJECTED,
        recommendation_data={},
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=rejected_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    bkg_tool = BookingTool(session=session, booking_service=booking_service)
    result = await bkg_tool.execute(
        {
            "recommendation_id": str(rec_id),
            "conversation_id": str(conv_id),
            "user_id": str(user_id),
            "selected_tier": "sedan",
        }
    )

    assert result.success is False
    assert "must be PENDING" in result.error


# ============================================================================
# 13. Graph Traversal Visited Nodes Parity
# ============================================================================


@pytest.mark.asyncio
async def test_13_graph_traversal_visited_nodes_parity():
    """Verify exact visited_nodes paths: Quoting vs Tier Selection vs Booking Confirmation."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_traversal_parity"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncSessionMock()
    session.add = MagicMock()

    pricing_service = CabPricingService(
        session=session, provider=DemoFleetPricingProvider()
    )
    rec_id = uuid.uuid4()
    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        return_value=mock_rec
    )
    rec_tool = RecommendationTool(session=session, cab_pricing_service=pricing_service)

    booking_service = BookingService(session)
    mock_bkg = Booking(
        id=uuid.uuid4(),
        recommendation_id=rec_id,
        booking_reference="BK-PARITY123",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
        booked_at=datetime.now(timezone.utc),
    )
    booking_service.create_booking_from_recommendation = AsyncMock(return_value=mock_bkg)
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    orchestrator, _ = _setup_orchestrator(
        session=session,
        booking_service=booking_service,
        checkpoint_manager=cp_manager,
        rec_tool=rec_tool,
    )

    # 1. Quoting Path (includes Tool)
    t1 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )
    assert t1["visited_nodes"] == [
        "start",
        "intent",
        "decision",
        "llm",
        "tool",
        "memory",
        "response",
        "end",
    ]

    # 2. Tier Selection Path (excludes Tool, prompts for confirmation)
    t2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Sedan",
        saved_locations=[mock_home, mock_work],
    )
    assert t2["visited_nodes"] == [
        "start",
        "intent",
        "decision",
        "llm",
        "memory",
        "response",
        "end",
    ]

    # 3. Booking Confirmation Path (includes Tool)
    t3 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Yes, confirm",
        saved_locations=[mock_home, mock_work],
    )
    assert t3["visited_nodes"] == [
        "start",
        "intent",
        "decision",
        "llm",
        "tool",
        "memory",
        "response",
        "end",
    ]


# ============================================================================
# 14. Stale Booking State Cleared on Route Change (Prevents Wrong Booking)
# ============================================================================


@pytest.mark.asyncio
async def test_14_stale_state_cleared_on_route_change_prevents_wrong_booking():
    """Verify selecting Sedan on Route A, then changing to Route B, does NOT allow immediate confirmation to book Route B with stale selection."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_stale_route_change"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncSessionMock()
    session.add = MagicMock()

    pricing_service = CabPricingService(
        session=session, provider=DemoFleetPricingProvider()
    )
    rec1_id = uuid.uuid4()
    mock_rec1 = Recommendation(
        id=rec1_id,
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    rec2_id = uuid.uuid4()
    mock_rec2 = Recommendation(
        id=rec2_id,
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        side_effect=[mock_rec1, mock_rec2]
    )
    rec_tool = RecommendationTool(session=session, cab_pricing_service=pricing_service)
    booking_service = BookingService(session)
    booking_service.create_booking_from_recommendation = AsyncMock()

    orchestrator, _ = _setup_orchestrator(
        session=session,
        booking_service=booking_service,
        checkpoint_manager=cp_manager,
        rec_tool=rec_tool,
    )

    # Turn 1: Quote Route A (Home -> Work)
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )

    # Turn 2: User selects Sedan on Route A
    t2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Sedan",
        saved_locations=[mock_home, mock_work],
    )
    ride2 = RideEntityState.model_validate(
        t2["final_state"].memory.extracted_entities["ride"]
    )
    assert ride2.selected_tier == "sedan"
    assert ride2.status == RideSlotStatus.AWAITING_CONFIRMATION

    # Turn 3: User changes route: "Book a cab from Work to Home"
    t3 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Work to Home",
        saved_locations=[mock_home, mock_work],
    )
    ride3 = RideEntityState.model_validate(
        t3["final_state"].memory.extracted_entities["ride"]
    )
    # Stale selected_tier and selected_fare MUST be cleared
    assert ride3.selected_tier is None
    assert ride3.selected_fare is None
    assert ride3.selected_display_name is None
    assert ride3.status == RideSlotStatus.RESOLVED

    # Turn 4: User says "Confirm" without choosing a tier for Route B
    t4 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Confirm",
        saved_locations=[mock_home, mock_work],
    )

    # Booking must NOT be invoked with the stale Sedan selection
    booking_service.create_booking_from_recommendation.assert_not_called()
    assert "Which vehicle option would you like to book?" in t4["content"]
    assert "tool" not in t4["visited_nodes"]


# ============================================================================
# 15. New Quote Requires Fresh Tier Selection and Confirmation
# ============================================================================


@pytest.mark.asyncio
async def test_15_new_quote_requires_fresh_tier_selection_and_confirmation():
    """Verify after route change, user explicitly selects SUV and confirms, successfully booking Route B."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_fresh_selection"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncSessionMock()
    session.add = MagicMock()

    pricing_service = CabPricingService(
        session=session, provider=DemoFleetPricingProvider()
    )
    rec1_id = uuid.uuid4()
    rec2_id = uuid.uuid4()
    mock_rec1 = Recommendation(
        id=rec1_id,
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    mock_rec2 = Recommendation(
        id=rec2_id,
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        side_effect=[mock_rec1, mock_rec2]
    )
    rec_tool = RecommendationTool(session=session, cab_pricing_service=pricing_service)

    booking_service = BookingService(session)
    mock_bkg = Booking(
        id=uuid.uuid4(),
        recommendation_id=rec2_id,
        booking_reference="BK-ROUTEB999",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
        booked_at=datetime.now(timezone.utc),
    )
    booking_service.create_booking_from_recommendation = AsyncMock(return_value=mock_bkg)
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec2)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    orchestrator, _ = _setup_orchestrator(
        session=session,
        booking_service=booking_service,
        checkpoint_manager=cp_manager,
        rec_tool=rec_tool,
    )

    # 1. Route A (Home -> Work)
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )
    # 2. Select Sedan
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Sedan",
        saved_locations=[mock_home, mock_work],
    )
    # 3. Change to Route B (Work -> Home)
    await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Work to Home",
        saved_locations=[mock_home, mock_work],
    )
    # 4. Fresh tier selection: SUV
    t4 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="SUV",
        saved_locations=[mock_home, mock_work],
    )
    ride4 = RideEntityState.model_validate(
        t4["final_state"].memory.extracted_entities["ride"]
    )
    assert ride4.selected_tier == "suv"
    assert ride4.status == RideSlotStatus.AWAITING_CONFIRMATION

    # 5. Confirm Route B SUV
    t5 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Yes, confirm",
        saved_locations=[mock_home, mock_work],
    )
    booking_service.create_booking_from_recommendation.assert_awaited_once_with(
        recommendation_id=rec2_id,
        provider="volta_fleet",
        external_booking_id=None,
    )
    assert "BK-ROUTEB999" in t5["content"]
    assert "Volta SUV" in t5["content"]


# ============================================================================
# 16. Missing User ID Rejected by BookingTool
# ============================================================================


@pytest.mark.asyncio
async def test_16_missing_user_id_rejected_by_booking_tool():
    """Verify BookingTool strictly rejects execution when user_id is missing or None."""
    session = AsyncSessionMock()
    booking_service = BookingService(session)
    bkg_tool = BookingTool(session=session, booking_service=booking_service)

    # Missing user_id entirely
    res1 = await bkg_tool.execute(
        {
            "recommendation_id": str(uuid.uuid4()),
            "conversation_id": str(uuid.uuid4()),
        }
    )
    assert res1.success is False
    assert "user_id" in res1.error

    # None user_id
    res2 = await bkg_tool.execute(
        {
            "recommendation_id": str(uuid.uuid4()),
            "conversation_id": str(uuid.uuid4()),
            "user_id": None,
        }
    )
    assert res2.success is False
    assert "user_id" in res2.error


# ============================================================================
# 17. Missing Conversation ID Rejected by BookingTool
# ============================================================================


@pytest.mark.asyncio
async def test_17_missing_conversation_id_rejected_by_booking_tool():
    """Verify BookingTool strictly rejects execution when conversation_id is missing or None."""
    session = AsyncSessionMock()
    booking_service = BookingService(session)
    bkg_tool = BookingTool(session=session, booking_service=booking_service)

    res1 = await bkg_tool.execute(
        {
            "recommendation_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
        }
    )
    assert res1.success is False
    assert "conversation_id" in res1.error

    res2 = await bkg_tool.execute(
        {
            "recommendation_id": str(uuid.uuid4()),
            "conversation_id": None,
            "user_id": str(uuid.uuid4()),
        }
    )
    assert res2.success is False
    assert "conversation_id" in res2.error


# ============================================================================
# 18. Invalid UUID Rejected by BookingTool
# ============================================================================


@pytest.mark.asyncio
async def test_18_invalid_uuid_rejected_by_booking_tool():
    """Verify BookingTool rejects malformed UUID strings for recommendation, conversation, or user."""
    session = AsyncSessionMock()
    booking_service = BookingService(session)
    bkg_tool = BookingTool(session=session, booking_service=booking_service)

    res_rec = await bkg_tool.execute(
        {
            "recommendation_id": "not-a-valid-uuid",
            "conversation_id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
        }
    )
    assert res_rec.success is False
    assert "recommendation_id" in res_rec.error

    res_conv = await bkg_tool.execute(
        {
            "recommendation_id": str(uuid.uuid4()),
            "conversation_id": "malformed-conv-id",
            "user_id": str(uuid.uuid4()),
        }
    )
    assert res_conv.success is False
    assert "conversation_id" in res_conv.error

    res_user = await bkg_tool.execute(
        {
            "recommendation_id": str(uuid.uuid4()),
            "conversation_id": str(uuid.uuid4()),
            "user_id": "invalid-user-uuid",
        }
    )
    assert res_user.success is False
    assert "user_id" in res_user.error


# ============================================================================
# 19. Valid Authenticated User and Conversation Completes Booking
# ============================================================================


@pytest.mark.asyncio
async def test_19_valid_authenticated_user_and_conversation_completes_booking():
    """Verify valid authenticated user and matching conversation successfully passes all checks and books."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    rec_id = uuid.uuid4()
    bkg_id = uuid.uuid4()

    session = AsyncSessionMock()
    booking_service = BookingService(session)

    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.PENDING,
        recommendation_data={
            "options": [
                {"tier": "sedan", "fare": 250, "display_name": "Volta Sedan"}
            ],
            "currency": "INR",
        },
    )
    mock_bkg = Booking(
        id=bkg_id,
        recommendation_id=rec_id,
        booking_reference="BK-AUTHVALID1",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
        booked_at=datetime.now(timezone.utc),
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )
    booking_service.create_booking_from_recommendation = AsyncMock(return_value=mock_bkg)

    bkg_tool = BookingTool(session=session, booking_service=booking_service)
    result = await bkg_tool.execute(
        {
            "recommendation_id": str(rec_id),
            "conversation_id": str(conv_id),
            "user_id": str(user_id),
            "selected_tier": "sedan",
        }
    )

    assert result.success is True
    assert result.data["booking_reference"] == "BK-AUTHVALID1"
    assert result.data["tier"] == "Volta Sedan"
    assert result.data["fare"] == 250
    booking_service.create_booking_from_recommendation.assert_awaited_once_with(
        recommendation_id=rec_id,
        provider="volta_fleet",
        external_booking_id=None,
    )


# ============================================================================
# 20. Booking Transaction Integrity & Rollback on Failure (Fix A)
# ============================================================================


@pytest.mark.asyncio
async def test_20_booking_service_transaction_rollback_on_notification_failure():
    """Verify that a failure in notification creation rolls back intermediate flushed state cleanly."""
    session = AsyncMock()
    session.add = MagicMock()
    service = BookingService(session)

    rec_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.PENDING,
    )
    service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    service.recommendation_repo.update = AsyncMock(return_value=mock_rec)

    mock_booking = Booking(id=uuid.uuid4(), recommendation_id=rec_id, booking_reference="BK-ROLLBACK1")
    service.booking_repo.create = AsyncMock(return_value=mock_booking)

    mock_conv = Conversation(id=conv_id, user_id=user_id)
    service.conversation_repo.get_by_id = AsyncMock(return_value=mock_conv)
    # Notification creation crashes
    service.notification_repo.create = AsyncMock(side_effect=RuntimeError("Notification channel crashed"))

    with pytest.raises(RuntimeError, match="Notification channel crashed"):
        await service.create_booking_from_recommendation(rec_id)

    # Rollback must be awaited to clear dirty / intermediate flushed entities
    session.rollback.assert_awaited_once()
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_21_booking_tool_rolls_back_session_on_unexpected_failure():
    """Verify that BookingTool triggers session.rollback() upon service error."""
    session = AsyncSessionMock()
    session.rollback = AsyncMock()
    booking_service = BookingService(session)

    rec_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )
    booking_service.create_booking_from_recommendation = AsyncMock(
        side_effect=RuntimeError("Disk I/O failure during commit")
    )

    bkg_tool = BookingTool(session=session, booking_service=booking_service)
    res = await bkg_tool.execute(
        {
            "recommendation_id": str(rec_id),
            "conversation_id": str(conv_id),
            "user_id": str(user_id),
            "selected_tier": "sedan",
        }
    )

    assert res.success is False
    assert "Disk I/O failure" in res.error
    session.rollback.assert_awaited()


# ============================================================================
# 21. Duplicate-Confirmation & Concurrency Hardening (Fix B)
# ============================================================================


@pytest.mark.asyncio
async def test_22_concurrent_duplicate_confirmation_status_race_resolves_idempotently():
    """Verify that if a concurrent confirmation wins and updates recommendation to ACCEPTED,
    the losing confirmation catches InvalidBookingStatusException, rolls back, and returns the existing booking.
    """
    session = AsyncSessionMock()
    session.rollback = AsyncMock()
    booking_service = BookingService(session)

    rec_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.PENDING,
        recommendation_data={"options": [{"tier": "sedan", "fare": 300, "display_name": "Volta Sedan"}]},
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    # When create_booking_from_recommendation is called, the winning transaction already committed,
    # so BookingService raises InvalidBookingStatusException (status is now ACCEPTED)
    booking_service.create_booking_from_recommendation = AsyncMock(
        side_effect=InvalidBookingStatusException("Recommendation status is 'ACCEPTED', must be PENDING.")
    )

    existing_booking = Booking(
        id=uuid.uuid4(),
        recommendation_id=rec_id,
        booking_reference="BK-CONCURRENT-WINNER",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
    )
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing_booking))
    )

    bkg_tool = BookingTool(session=session, booking_service=booking_service)
    res = await bkg_tool.execute(
        {
            "recommendation_id": str(rec_id),
            "conversation_id": str(conv_id),
            "user_id": str(user_id),
            "selected_tier": "sedan",
        }
    )

    assert res.success is True
    assert res.data["booking_reference"] == "BK-CONCURRENT-WINNER"
    assert res.data["is_duplicate_replay"] is True
    session.rollback.assert_awaited()


@pytest.mark.asyncio
async def test_23_concurrent_duplicate_confirmation_integrity_collision_resolves_idempotently():
    """Verify that when concurrent inserts collide on unique constraint uq_bookings_recommendation_id,
    the losing request catches IntegrityError, rolls back, and resolves to the existing booking.
    """
    from sqlalchemy.exc import IntegrityError

    session = AsyncSessionMock()
    session.rollback = AsyncMock()
    booking_service = BookingService(session)

    rec_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    # Simulate database unique constraint violation
    booking_service.create_booking_from_recommendation = AsyncMock(
        side_effect=IntegrityError("duplicate key value violates unique constraint 'uq_bookings_recommendation_id'", params={}, orig=Exception())
    )

    existing_booking = Booking(
        id=uuid.uuid4(),
        recommendation_id=rec_id,
        booking_reference="BK-UNIQUE-RECOVERED",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
    )
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing_booking))
    )

    bkg_tool = BookingTool(session=session, booking_service=booking_service)
    res = await bkg_tool.execute(
        {
            "recommendation_id": str(rec_id),
            "conversation_id": str(conv_id),
            "user_id": str(user_id),
            "selected_tier": "sedan",
        }
    )

    assert res.success is True
    assert res.data["booking_reference"] == "BK-UNIQUE-RECOVERED"
    assert res.data["is_duplicate_replay"] is True
    session.rollback.assert_awaited()


@pytest.mark.asyncio
async def test_24_pessimistic_locking_in_create_booking_from_recommendation():
    """Verify BookingService.create_booking_from_recommendation requests row lock (with_for_update=True)."""
    session = AsyncMock()
    session.add = MagicMock()
    service = BookingService(session)

    rec_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.PENDING,
    )
    service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    service.recommendation_repo.update = AsyncMock(return_value=mock_rec)

    mock_booking = Booking(id=uuid.uuid4(), recommendation_id=rec_id, booking_reference="BK-LOCKTEST1")
    service.booking_repo.create = AsyncMock(return_value=mock_booking)

    mock_conv = Conversation(id=conv_id, user_id=user_id)
    service.conversation_repo.get_by_id = AsyncMock(return_value=mock_conv)
    service.notification_repo.create = AsyncMock(return_value=MagicMock())

    await service.create_booking_from_recommendation(rec_id)

    # Ensure get_by_id was called with with_for_update=True
    service.recommendation_repo.get_by_id.assert_awaited_once_with(rec_id, with_for_update=True)


def test_25_database_unique_constraint_on_recommendation_id():
    """Verify that Booking entity metadata defines the uq_bookings_recommendation_id constraint."""
    constraint_names = [c.name for c in Booking.__table__.constraints]
    assert "uq_bookings_recommendation_id" in constraint_names

    # Verify column uniqueness property
    unique_constraint = next(c for c in Booking.__table__.constraints if c.name == "uq_bookings_recommendation_id")
    col_names = [col.name for col in unique_constraint.columns]
    assert col_names == ["recommendation_id"]


def test_26_live_database_unique_constraint_enforcement():
    """Verify SQLite database engine enforces uniqueness on recommendation_id while permitting multiple NULLs."""
    from app.db.base import Base
    from sqlalchemy import create_engine
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm import Session

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    rec_id = uuid.uuid4()
    bkg1 = Booking(
        id=uuid.uuid4(),
        recommendation_id=rec_id,
        booking_reference="BK-LIVE-001",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
    )
    bkg2_dup = Booking(
        id=uuid.uuid4(),
        recommendation_id=rec_id,
        booking_reference="BK-LIVE-002",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
    )
    bkg_null1 = Booking(
        id=uuid.uuid4(),
        recommendation_id=None,
        booking_reference="BK-LIVE-003",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
    )
    bkg_null2 = Booking(
        id=uuid.uuid4(),
        recommendation_id=None,
        booking_reference="BK-LIVE-004",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
    )

    with Session(engine) as db:
        # First booking succeeds
        db.add(bkg1)
        db.commit()

        # Second booking with same recommendation_id must violate unique constraint
        db.add(bkg2_dup)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        # Multiple bookings with recommendation_id=None are permitted
        db.add(bkg_null1)
        db.commit()
        db.add(bkg_null2)
        db.commit()


# ============================================================================
# 22. Booking Replay Response Consistency & Tier Integrity
# ============================================================================


@pytest.mark.asyncio
async def test_27_sequential_replay_with_different_tier_does_not_echo_or_misrepresent():
    """Verify that replaying a booking with a different incoming selected_tier does NOT echo
    the new tier or invent fare information, returning tier=None, fare=None, and is_duplicate_replay=True.
    """
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    rec_id = uuid.uuid4()

    session = AsyncSessionMock()
    booking_service = BookingService(session)

    # Recommendation already ACCEPTED
    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.ACCEPTED,
        recommendation_data={
            "currency": "INR",
            "options": [
                {"tier": "sedan", "fare": 350, "display_name": "Volta Sedan"},
                {"tier": "suv", "fare": 550, "display_name": "Volta SUV"},
            ],
        },
    )
    existing_bkg = Booking(
        id=uuid.uuid4(),
        recommendation_id=rec_id,
        booking_reference="BK-SEDAN-ORIGINAL",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
        booked_at=datetime.now(timezone.utc),
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing_bkg))
    )
    booking_service.create_booking_from_recommendation = AsyncMock()

    bkg_tool = BookingTool(session=session, booking_service=booking_service)
    # Incoming replay request attempts to claim a different tier ("suv")
    res = await bkg_tool.execute(
        {
            "recommendation_id": str(rec_id),
            "conversation_id": str(conv_id),
            "user_id": str(user_id),
            "selected_tier": "suv",
        }
    )

    assert res.success is True
    assert res.data["is_duplicate_replay"] is True
    assert res.data["booking_reference"] == "BK-SEDAN-ORIGINAL"
    # Must NOT echo the replayed tier ("suv") or claim its fare (550)
    assert res.data["tier"] is None
    assert res.data["fare"] is None
    assert res.data["currency"] == "INR"
    booking_service.create_booking_from_recommendation.assert_not_called()


@pytest.mark.asyncio
async def test_28_concurrent_race_replay_with_different_tier_does_not_echo_tier():
    """Verify concurrent race replay (InvalidBookingStatusException) with a different incoming tier
    does not echo or misrepresent the tier.
    """
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    rec_id = uuid.uuid4()

    session = AsyncSessionMock()
    session.rollback = AsyncMock()
    booking_service = BookingService(session)

    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.PENDING,
        recommendation_data={"options": [{"tier": "sedan", "fare": 300}]},
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    booking_service.create_booking_from_recommendation = AsyncMock(
        side_effect=InvalidBookingStatusException(
            "Recommendation status is 'ACCEPTED', must be PENDING."
        )
    )

    existing_booking = Booking(
        id=uuid.uuid4(),
        recommendation_id=rec_id,
        booking_reference="BK-RACE-WINNER",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
        booked_at=datetime.now(timezone.utc),
    )
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing_booking))
    )

    bkg_tool = BookingTool(session=session, booking_service=booking_service)
    # Incoming request attempts tier "auto"
    res = await bkg_tool.execute(
        {
            "recommendation_id": str(rec_id),
            "conversation_id": str(conv_id),
            "user_id": str(user_id),
            "selected_tier": "auto",
        }
    )

    assert res.success is True
    assert res.data["booking_reference"] == "BK-RACE-WINNER"
    assert res.data["is_duplicate_replay"] is True
    assert res.data["tier"] is None
    assert res.data["fare"] is None
    session.rollback.assert_awaited()


@pytest.mark.asyncio
async def test_29_concurrent_integrity_collision_replay_with_different_tier_does_not_echo_tier():
    """Verify concurrent integrity collision replay with a different incoming tier
    does not echo or misrepresent the tier.
    """
    from sqlalchemy.exc import IntegrityError

    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    rec_id = uuid.uuid4()

    session = AsyncSessionMock()
    session.rollback = AsyncMock()
    booking_service = BookingService(session)

    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    booking_service.create_booking_from_recommendation = AsyncMock(
        side_effect=IntegrityError("duplicate key", params={}, orig=Exception())
    )

    existing_booking = Booking(
        id=uuid.uuid4(),
        recommendation_id=rec_id,
        booking_reference="BK-COLLISION-WINNER",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
        booked_at=datetime.now(timezone.utc),
    )
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=existing_booking))
    )

    bkg_tool = BookingTool(session=session, booking_service=booking_service)
    # Incoming request attempts tier "premium_suv"
    res = await bkg_tool.execute(
        {
            "recommendation_id": str(rec_id),
            "conversation_id": str(conv_id),
            "user_id": str(user_id),
            "selected_tier": "premium_suv",
        }
    )

    assert res.success is True
    assert res.data["booking_reference"] == "BK-COLLISION-WINNER"
    assert res.data["is_duplicate_replay"] is True
    assert res.data["tier"] is None
    assert res.data["fare"] is None
    session.rollback.assert_awaited()


# ============================================================================
# 23. Duplicate-Booking Replay Response Path Fix (ToolNode & ResponseNode)
# ============================================================================


@pytest.mark.asyncio
async def test_30_tool_node_duplicate_replay_state_update():
    """Verify ToolNode clears unverified tier/fare and sets is_duplicate_replay=True on duplicate replay."""
    from app.ai.models import AIToolResult
    from app.context.state import ConversationData, ConversationState
    from app.workflow.nodes.tool_node import ToolNode

    conv_id = uuid.uuid4()
    user_id = uuid.uuid4()
    rec_id = uuid.uuid4()
    booking_id = uuid.uuid4()

    mock_dispatcher = MagicMock()
    mock_dispatcher.dispatch = AsyncMock(
        return_value=AIToolResult(
            tool_name="booking",
            success=True,
            data={
                "booking_id": str(booking_id),
                "booking_reference": "BK-REPLAY-001",
                "booking_status": "confirmed",
                "tier": None,
                "fare": None,
                "is_duplicate_replay": True,
            },
        )
    )

    tool_node = ToolNode(node_id="tool", tool_dispatcher=mock_dispatcher)

    initial_ride = {
        "recommendation_id": str(rec_id),
        "selected_tier": "suv",
        "selected_display_name": "Volta SUV",
        "selected_fare": 550,
        "status": "awaiting_confirmation",
    }
    state = ConversationState(
        conversation=ConversationData(
            conversation_id=conv_id,
            user_id=str(user_id),
            current_message={"role": "user", "content": "Confirm"},
        )
    ).with_update(
        detected_intent={"requires_booking": True},
        extracted_entities={"ride": initial_ride},
    )

    updated_state = await tool_node.execute(state)
    ride_res = updated_state.memory.extracted_entities.get("ride", {})

    # Existing booking reference and status preserved
    assert ride_res.get("booking_reference") == "BK-REPLAY-001"
    assert ride_res.get("booking_id") == str(booking_id)
    assert ride_res.get("booking_status") == "confirmed"
    assert ride_res.get("is_booked") is True
    # Replay flag explicitly persisted
    assert ride_res.get("is_duplicate_replay") is True
    # Unverified selection fields must be cleared, not echoing incoming 'suv' or 550
    assert ride_res.get("selected_tier") is None
    assert ride_res.get("selected_display_name") is None
    assert ride_res.get("selected_fare") is None


@pytest.mark.asyncio
async def test_31_response_node_duplicate_replay_formatting():
    """Verify ResponseNode formats replay confirmations without claiming vehicle tier or stale fare."""
    from app.context.state import ConversationData, ConversationState
    from app.workflow.nodes.response_node import ResponseNode

    conv_id = uuid.uuid4()
    user_id = uuid.uuid4()

    response_node = ResponseNode(node_id="response")

    ride_replay_state = {
        "booking_reference": "BK-REPLAY-002",
        "booking_status": "confirmed",
        "is_booked": True,
        "is_duplicate_replay": True,
        "selected_tier": None,
        "selected_display_name": None,
        "selected_fare": None,
        "pickup_raw": "Indiranagar",
        "destination_raw": "Whitefield",
    }
    state = ConversationState(
        conversation=ConversationData(
            conversation_id=conv_id,
            user_id=str(user_id),
            current_message={"role": "user", "content": "Confirm"},
        )
    ).with_update(
        extracted_entities={"ride": ride_replay_state},
        node_results={"tool": {"executed": True}},
    )

    final_state = await response_node.execute(state)
    resp = final_state.execution.node_results.get("response", {})
    content = resp.get("content", "")

    # States existing booking is already confirmed
    assert "This ride has already been confirmed." in content
    assert "BK-REPLAY-002" in content
    assert "Status: Confirmed" in content
    assert "Route: Indiranagar to Whitefield" in content

    # Must NOT claim a vehicle tier or quoted fare
    assert "Vehicle Tier:" not in content
    assert "Quoted Fare:" not in content
    assert "suv" not in content.lower()
    assert "sedan" not in content.lower()
    assert "successfully booked" not in content.lower()


@pytest.mark.asyncio
async def test_32_workflow_duplicate_replay_with_different_tier_does_not_echo_tier_or_fare():
    """Verify end-to-end chat turn on duplicate replay with different tier does not mention incoming tier or stale fare."""
    from app.context.state import ConversationData, ConversationState

    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_replay_tier_mismatch"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncSessionMock()
    session.add = MagicMock()

    pricing_service = CabPricingService(
        session=session, provider=DemoFleetPricingProvider()
    )
    rec_id = uuid.uuid4()
    mock_rec = Recommendation(
        id=rec_id,
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={
            "currency": "INR",
            "options": [
                {"tier": "sedan", "fare": 300, "display_name": "Volta Sedan"},
                {"tier": "suv", "fare": 500, "display_name": "Volta SUV"},
            ],
        },
    )
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        return_value=mock_rec
    )
    rec_tool = RecommendationTool(session=session, cab_pricing_service=pricing_service)

    booking_service = BookingService(session)
    booking_id = uuid.uuid4()
    mock_bkg = Booking(
        id=booking_id,
        recommendation_id=rec_id,
        booking_reference="BK-ORIGINAL-SEDAN",
        booking_status=BookingStatus.CONFIRMED,
        provider="volta_fleet",
        booked_at=datetime.now(timezone.utc),
    )
    # First booking creates original booking
    booking_service.create_booking_from_recommendation = AsyncMock(
        return_value=mock_bkg
    )
    booking_service.recommendation_repo.get_by_id = AsyncMock(return_value=mock_rec)
    booking_service.conversation_repo.get_by_id = AsyncMock(
        return_value=Conversation(id=conv_id, user_id=user_id)
    )

    orchestrator, _ = _setup_orchestrator(
        session=session,
        booking_service=booking_service,
        checkpoint_manager=cp_manager,
        rec_tool=rec_tool,
    )

    # 1. Quoting Turn
    t1 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )
    assert t1["recommendation_id"] is not None

    # 2. Select Sedan
    t2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Volta Sedan",
        saved_locations=[mock_home, mock_work],
    )
    assert "Would you like to confirm this booking?" in t2["content"]

    # 3. Confirm Sedan (first-time booking)
    t3 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Yes, confirm",
        saved_locations=[mock_home, mock_work],
    )
    assert "Your Volta Sedan ride has been successfully booked!" in t3["content"]
    assert "BK-ORIGINAL-SEDAN" in t3["content"]
    assert "Vehicle Tier: Volta Sedan" in t3["content"]
    assert "Quoted Fare: INR 240.00" in t3["content"]

    # 4. Replay arrives: Now recommendation is ACCEPTED.
    mock_rec.status = RecommendationStatus.ACCEPTED
    session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=mock_bkg))
    )

    # Replay confirmation with incoming tier='suv'
    replay_ride = {
        "recommendation_id": str(rec_id),
        "selected_tier": "suv",
        "selected_display_name": "Volta SUV",
        "selected_fare": 500,
        "available_options": mock_rec.recommendation_data["options"],
        "status": "awaiting_confirmation",
        "pickup_point": {"label": "Home"},
        "destination_point": {"label": "Work"},
    }
    replay_state = ConversationState(
        conversation=ConversationData(
            conversation_id=conv_id,
            user_id=str(user_id),
            current_message={"role": "user", "content": "Yes, confirm"},
        )
    ).with_update(
        detected_intent={"requires_booking": True},
        extracted_entities={"ride": replay_ride},
    )

    graph = orchestrator.build_graph()
    exec_result = await orchestrator.executor.execute(graph, replay_state)
    final_resp = exec_result.final_state.execution.node_results.get("response", {})
    replay_content = final_resp.get("content", "")

    # Assert replay response
    assert "This ride has already been confirmed." in replay_content
    assert "BK-ORIGINAL-SEDAN" in replay_content
    assert "Status: Confirmed" in replay_content
    assert "Route: Home to Work" in replay_content
    # Must NOT echo 'Volta SUV' or 500
    assert "Volta SUV" not in replay_content
    assert "SUV" not in replay_content
    assert "500" not in replay_content
    assert "Quoted Fare" not in replay_content


@pytest.mark.asyncio
async def test_33_normal_booking_preserves_tier_and_fare():
    """Verify normal first-time booking output still displays selected tier and fare."""
    from app.context.state import ConversationData, ConversationState
    from app.workflow.nodes.response_node import ResponseNode

    conv_id = uuid.uuid4()
    user_id = uuid.uuid4()

    response_node = ResponseNode(node_id="response")

    ride_normal_state = {
        "booking_reference": "BK-FIRST-TIME",
        "booking_status": "confirmed",
        "is_booked": True,
        "is_duplicate_replay": False,
        "selected_tier": "sedan",
        "selected_display_name": "Volta Sedan",
        "selected_fare": 350,
        "pickup_raw": "Airport",
        "destination_raw": "Hotel",
    }
    state = ConversationState(
        conversation=ConversationData(
            conversation_id=conv_id,
            user_id=str(user_id),
            current_message={"role": "user", "content": "Confirm"},
        )
    ).with_update(
        extracted_entities={"ride": ride_normal_state},
        node_results={"tool": {"executed": True}},
    )

    final_state = await response_node.execute(state)
    resp = final_state.execution.node_results.get("response", {})
    content = resp.get("content", "")

    # First-time confirmation format must be preserved
    assert "Your Volta Sedan ride has been successfully booked!" in content
    assert "BK-FIRST-TIME" in content
    assert "Status: Confirmed" in content
    assert "Vehicle Tier: Volta Sedan" in content
    assert "Quoted Fare: INR 350" in content
    assert "Route: Airport to Hotel" in content


