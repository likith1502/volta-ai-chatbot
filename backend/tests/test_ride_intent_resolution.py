import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.ai.base import AIProvider
from app.ai.models import AIRequest, AIResponse, AITokenUsage
from app.ai.prompts.prompt_builder import PromptBuilder
from app.ai.prompts.recommendation import (
    is_cancellation_intent,
    is_knowledge_base_query,
    is_ride_intent,
)
from app.ai.tools.dispatcher import AIToolDispatcher
from app.ai.tools.recommendation_tool import RecommendationTool
from app.ai.tools.registry import AIToolRegistry
from app.checkpoints.checkpoint_manager import CheckpointManager
from app.checkpoints.checkpoint_store import InMemoryCheckpointStore
from app.fleet.demo import DemoFleetPricingProvider
from app.models.recommendation import Recommendation, RecommendationStatus
from app.models.saved_location import SavedLocation
from app.schemas.cab import LocationPoint
from app.schemas.ride import RideEntityState, RideSlotStatus
from app.services.cab_pricing import CabPricingService
from app.services.chat_graph import ChatGraphOrchestrator
from app.workflow.nodes.entity_node import RideEntityResolver


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


# ============================================================================
# 1. Single-Turn Resolved Ride Request
# ============================================================================


@pytest.mark.asyncio
async def test_01_full_ride_request_single_turn_resolved():
    """Verify single-turn request 'Book a cab from Home to Work' resolves both slots and dispatches pricing."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_single_turn"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    session = AsyncMock()
    session.add = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    session.execute = AsyncMock(
        return_value=MagicMock(scalars=MagicMock(return_value=mock_scalars))
    )

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
    registry = AIToolRegistry()
    registry.register(rec_tool)
    dispatcher = AIToolDispatcher(registry)

    orchestrator = ChatGraphOrchestrator(
        provider=MockDeterministicAIProvider(),
        tool_dispatcher=dispatcher,
        checkpoint_manager=CheckpointManager(store=InMemoryCheckpointStore()),
    )

    result = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book a cab from Home to Work",
        saved_locations=[mock_home, mock_work],
    )

    final_state = result["final_state"]
    ride_state = RideEntityState.model_validate(
        final_state.memory.extracted_entities["ride"]
    )

    assert ride_state.status == RideSlotStatus.RESOLVED
    assert ride_state.is_complete is True
    assert ride_state.pickup_point is not None
    assert ride_state.pickup_point.saved_location_id == mock_home.id
    assert ride_state.pickup_point.label == "Home"
    assert ride_state.pickup_point.address == mock_home.address
    assert ride_state.destination_point is not None
    assert ride_state.destination_point.saved_location_id == mock_work.id
    assert ride_state.destination_point.label == "Work"
    assert ride_state.destination_point.address == mock_work.address

    # Graph Traversal includes Tool Node
    assert result["visited_nodes"] == [
        "start",
        "intent",
        "decision",
        "llm",
        "tool",
        "memory",
        "response",
        "end",
    ]
    assert "tool" in result["visited_nodes"]
    assert result["recommendation_id"] is not None
    assert "Here are the cars available for your trip:" in result["content"]


# ============================================================================
# 2. Multi-Turn Slot Filling (Pickup First, Then Destination)
# ============================================================================


@pytest.mark.asyncio
async def test_02_multi_turn_pickup_first_then_destination():
    """Verify multi-turn request collects pickup first, prompts for destination, then resolves upon destination."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_multi_turn_1"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_store = InMemoryCheckpointStore()
    cp_manager = CheckpointManager(store=cp_store)

    session = AsyncMock()
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
    registry = AIToolRegistry()
    registry.register(rec_tool)
    dispatcher = AIToolDispatcher(registry)

    orchestrator = ChatGraphOrchestrator(
        provider=MockDeterministicAIProvider(),
        tool_dispatcher=dispatcher,
        checkpoint_manager=cp_manager,
    )

    # Turn 1: User provides only pickup
    turn1_result = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="I need a ride from Home",
        saved_locations=[mock_home, mock_work],
    )

    assert turn1_result["recommendation_id"] is None
    assert turn1_result["visited_nodes"] == [
        "start",
        "intent",
        "decision",
        "llm",
        "memory",
        "response",
        "end",
    ]
    assert "tool" not in turn1_result["visited_nodes"]
    assert "Where would you like to go from Home?" in turn1_result["content"]

    turn1_ride = RideEntityState.model_validate(
        turn1_result["final_state"].memory.extracted_entities["ride"]
    )
    assert turn1_ride.status == RideSlotStatus.NEEDS_DESTINATION
    assert turn1_ride.pickup_point.saved_location_id == mock_home.id
    assert turn1_ride.destination_point is None

    # Turn 2: User answers with destination
    turn2_result = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="To Work",
        saved_locations=[mock_home, mock_work],
    )

    assert turn2_result["recommendation_id"] is not None
    assert turn2_result["visited_nodes"] == [
        "start",
        "intent",
        "decision",
        "llm",
        "tool",
        "memory",
        "response",
        "end",
    ]
    turn2_ride = RideEntityState.model_validate(
        turn2_result["final_state"].memory.extracted_entities["ride"]
    )
    assert turn2_ride.status == RideSlotStatus.RESOLVED
    assert turn2_ride.pickup_point.saved_location_id == mock_home.id
    assert turn2_ride.destination_point.saved_location_id == mock_work.id


# ============================================================================
# 3. Multi-Turn Slot Filling (Destination First, Then Pickup)
# ============================================================================


@pytest.mark.asyncio
async def test_03_multi_turn_destination_first_then_pickup():
    """Verify multi-turn request collects destination first, prompts for pickup, then completes."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_multi_turn_2"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_store = InMemoryCheckpointStore()
    cp_manager = CheckpointManager(store=cp_store)

    session = AsyncMock()
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
    registry = AIToolRegistry()
    registry.register(rec_tool)
    dispatcher = AIToolDispatcher(registry)

    orchestrator = ChatGraphOrchestrator(
        provider=MockDeterministicAIProvider(),
        tool_dispatcher=dispatcher,
        checkpoint_manager=cp_manager,
    )

    # Turn 1: User provides only destination
    turn1 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Get me a car to the airport",
        saved_locations=[mock_home, mock_work],
    )

    assert turn1["recommendation_id"] is None
    assert (
        "Where would you like to be picked up from to go to airport?"
        in turn1["content"]
    )
    ride1 = RideEntityState.model_validate(
        turn1["final_state"].memory.extracted_entities["ride"]
    )
    assert ride1.status == RideSlotStatus.NEEDS_PICKUP
    assert ride1.destination_point.label == "airport"
    assert ride1.pickup_point is None

    # Turn 2: User provides pickup
    turn2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="From Home",
        saved_locations=[mock_home, mock_work],
    )

    assert turn2["recommendation_id"] is not None
    ride2 = RideEntityState.model_validate(
        turn2["final_state"].memory.extracted_entities["ride"]
    )
    assert ride2.status == RideSlotStatus.RESOLVED
    assert ride2.pickup_point.saved_location_id == mock_home.id
    assert ride2.destination_point.label == "airport"


# ============================================================================
# 4. Multi-Turn Slot Filling (Neither Provided First Turn)
# ============================================================================


@pytest.mark.asyncio
async def test_04_multi_turn_neither_provided_then_complete():
    """Verify 'Book me a cab' initiates slot filling with status NEEDS_BOTH, then resolves in turn 2."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_multi_turn_3"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    session = AsyncMock()
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
    registry = AIToolRegistry()
    registry.register(rec_tool)
    dispatcher = AIToolDispatcher(registry)

    orchestrator = ChatGraphOrchestrator(
        provider=MockDeterministicAIProvider(),
        tool_dispatcher=dispatcher,
        checkpoint_manager=cp_manager,
    )

    # Turn 1: Neither pickup nor destination
    turn1 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Book me a cab",
        saved_locations=[mock_home, mock_work],
    )

    assert turn1["recommendation_id"] is None
    assert (
        "Where would you like to be picked up and where are you heading?"
        in turn1["content"]
    )
    ride1 = RideEntityState.model_validate(
        turn1["final_state"].memory.extracted_entities["ride"]
    )
    assert ride1.status == RideSlotStatus.NEEDS_BOTH

    # Turn 2: User provides both
    turn2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="From Home to Work",
        saved_locations=[mock_home, mock_work],
    )

    assert turn2["recommendation_id"] is not None
    ride2 = RideEntityState.model_validate(
        turn2["final_state"].memory.extracted_entities["ride"]
    )
    assert ride2.status == RideSlotStatus.RESOLVED


# ============================================================================
# 5. Saved Location Resolution Case-Insensitivity & Canonicalization
# ============================================================================


@pytest.mark.asyncio
async def test_05_saved_locations_case_insensitivity_and_whitespace():
    """Verify saved locations match case-insensitively with leading/trailing whitespace."""
    user_id = uuid.uuid4()
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    point_home = await RideEntityResolver.resolve_location_point(
        raw_str="  home  ",
        saved_locations=[mock_home, mock_work],
        user_id=user_id,
    )
    assert point_home is not None
    assert point_home.saved_location_id == mock_home.id
    assert point_home.label == "Home"

    point_work = await RideEntityResolver.resolve_location_point(
        raw_str="WORK",
        saved_locations=[mock_home, mock_work],
        user_id=user_id,
    )
    assert point_work is not None
    assert point_work.saved_location_id == mock_work.id
    assert point_work.label == "Work"


# ============================================================================
# 6. Unsaved Locations: Clean Text, No Fabricated Coordinates
# ============================================================================


@pytest.mark.asyncio
async def test_06_unsaved_locations_preserve_raw_text_no_fabricated_coordinates():
    """Verify arbitrary locations retain cleaned labels without inventing latitude/longitude."""
    point = await RideEntityResolver.resolve_location_point(
        raw_str="Central Railway Station, Platform 1",
        saved_locations=[],
        user_id=uuid.uuid4(),
    )
    assert point is not None
    assert point.saved_location_id is None
    assert point.latitude is None
    assert point.longitude is None
    assert point.label == "Central Railway Station, Platform 1"
    assert point.address == "Central Railway Station, Platform 1"


# ============================================================================
# 7. Slot Corrections and Overrides Mid-Conversation
# ============================================================================


@pytest.mark.asyncio
async def test_07_slot_override_mid_conversation():
    """Verify user can update previously collected pickup location with an override phrase."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_override"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    orchestrator = ChatGraphOrchestrator(
        provider=MockDeterministicAIProvider(),
        checkpoint_manager=cp_manager,
    )

    # Turn 1: Pickup Home
    turn1 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="I need a ride from Home",
        saved_locations=[mock_home, mock_work],
    )
    ride1 = RideEntityState.model_validate(
        turn1["final_state"].memory.extracted_entities["ride"]
    )
    assert ride1.pickup_point.label == "Home"

    # Turn 2: User overrides pickup to Work instead
    turn2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Actually, pick me up at Work instead",
        saved_locations=[mock_home, mock_work],
    )
    ride2 = RideEntityState.model_validate(
        turn2["final_state"].memory.extracted_entities["ride"]
    )
    assert ride2.pickup_point.label == "Work"
    assert ride2.pickup_point.saved_location_id == mock_work.id
    assert ride2.destination_point is None
    assert "Where would you like to go from Work?" in turn2["content"]


# ============================================================================
# 8. Ride Cancellation Mid-Conversation
# ============================================================================


@pytest.mark.asyncio
async def test_08_cancellation_mid_conversation():
    """Verify user saying 'cancel ride' aborts the active request without invoking tools."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_cancel"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    mock_dispatcher = MagicMock()
    mock_dispatcher.dispatch = AsyncMock()

    orchestrator = ChatGraphOrchestrator(
        provider=MockDeterministicAIProvider(),
        tool_dispatcher=mock_dispatcher,
        checkpoint_manager=cp_manager,
    )

    # Turn 1: Start request
    turn1 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Get me a car to the airport",
        saved_locations=[mock_home, mock_work],
    )
    assert (
        turn1["final_state"].memory.extracted_entities["ride"]["status"]
        == "needs_pickup"
    )

    # Turn 2: Cancel
    turn2 = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="Cancel ride",
        saved_locations=[mock_home, mock_work],
    )

    ride2 = RideEntityState.model_validate(
        turn2["final_state"].memory.extracted_entities["ride"]
    )
    assert ride2.status == RideSlotStatus.CANCELLED
    assert ride2.is_cancelled is True
    assert "Your ride request has been cancelled" in turn2["content"]
    assert turn2["recommendation_id"] is None
    assert not mock_dispatcher.dispatch.called


# ============================================================================
# 9. Multiple Cancellation Keyword Variants
# ============================================================================


def test_09_other_cancellation_phrases():
    """Verify varied conversational cancellation phrases are recognized."""
    cancellation_phrases = [
        "cancel",
        "never mind",
        "nevermind",
        "stop",
        "cancel the ride",
        "cancel my booking",
        "forget it",
    ]
    for phrase in cancellation_phrases:
        assert is_cancellation_intent(phrase) is True, f"Failed for phrase: '{phrase}'"


# ============================================================================
# 10. Identical Pickup and Destination Rejected
# ============================================================================


@pytest.mark.asyncio
async def test_10_identical_pickup_and_destination_rejected():
    """Verify attempting to book a ride from Work to Work is rejected and requests a new destination."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    orchestrator = ChatGraphOrchestrator(
        provider=MockDeterministicAIProvider(),
        checkpoint_manager=CheckpointManager(store=InMemoryCheckpointStore()),
    )

    result = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id="sess_identical",
        message_text="Book a cab from Work to Work",
        saved_locations=[mock_home, mock_work],
    )

    ride = RideEntityState.model_validate(
        result["final_state"].memory.extracted_entities["ride"]
    )
    assert ride.status == RideSlotStatus.NEEDS_DESTINATION
    assert ride.destination_point is None
    assert "cannot both be Work" in result["content"]
    assert result["recommendation_id"] is None


# ============================================================================
# 11. False Positives Rejection (Conversational Phrases)
# ============================================================================


def test_11_false_positives_rejection():
    """Verify conversational messages containing 'go', 'take', or 'home' are not classified as ride requests."""
    non_ride_messages = [
        "I want to go home",
        "I just want to go home",
        "Take care",
        "Take your time",
        "Home is where the heart is",
        "Let's go",
        "Take note of this update",
        "What is the battery range?",
    ]
    for msg in non_ride_messages:
        assert is_ride_intent(msg, has_pending_request=False) is False, (
            f"False positive on: '{msg}'"
        )


# ============================================================================
# 12. Knowledge-Base Routing (Cancellation Policy vs Ride Cancellation)
# ============================================================================


def test_12_knowledge_base_cancellation_policy_not_ride_intent():
    """Verify questions about cancellation policy route to KB/conversation, NOT ride cancellation."""
    kb_queries = [
        "What is VOLTA's cancellation policy?",
        "Tell me about the cancellation policy",
        "Can you explain the refund policy?",
        "How much does a ride cost?",
        "What vehicles do you have?",
    ]
    for query in kb_queries:
        assert is_knowledge_base_query(query) is True, (
            f"Failed KB query check: '{query}'"
        )
        assert is_cancellation_intent(query) is False, (
            f"False cancellation on: '{query}'"
        )
        assert is_ride_intent(query, has_pending_request=False) is False, (
            f"False ride intent on: '{query}'"
        )


# ============================================================================
# 13. User Isolation Enforcement (No Cross-User Saved Location Leak)
# ============================================================================


@pytest.mark.asyncio
async def test_13_user_isolation_prevent_cross_user_saved_location_leak():
    """Verify User B cannot access or resolve User A's private saved location records."""
    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()
    mock_home_a, _ = _create_mock_saved_locations(user_a_id)

    # User B has no saved locations
    point_b = await RideEntityResolver.resolve_location_point(
        raw_str="Home",
        saved_locations=[],  # User B's locations
        user_id=user_b_id,
    )

    assert point_b is not None
    assert point_b.saved_location_id is None
    assert point_b.latitude is None
    assert point_b.longitude is None
    assert (
        point_b.address == "Home"
    )  # Fallback to string, no leak of User A's private address


# ============================================================================
# 14. CabPricingService Integration and Recommendation Persistence
# ============================================================================


@pytest.mark.asyncio
async def test_14_step3_cab_pricing_integration_and_recommendation_persistence():
    """Verify CabPricingService generates structured options and persists single recommendation without booking."""
    session = AsyncMock()
    conv_id = uuid.uuid4()
    mock_rec = Recommendation(
        id=uuid.uuid4(),
        conversation_id=conv_id,
        recommendation_type="cab_availability",
        status=RecommendationStatus.PENDING,
        recommendation_data={},
    )
    pricing_service = CabPricingService(session=session)
    pricing_service.recommendation_service.create_recommendation = AsyncMock(
        return_value=mock_rec
    )

    quote = await pricing_service.get_availability_quote(
        pickup=LocationPoint(label="Work"),
        destination=LocationPoint(label="Home"),
        conversation_id=conv_id,
        persist_recommendation=True,
    )

    assert quote.recommendation_id == mock_rec.id
    assert len(quote.options) == 5
    assert all(opt.fare > Decimal("0.00") for opt in quote.options)
    assert quote.currency == "INR"
    pricing_service.recommendation_service.create_recommendation.assert_awaited_once()


# ============================================================================
# 15. Privacy Boundary: LLM Prompt Injects Only Labels
# ============================================================================


def test_15_privacy_llm_prompt_no_raw_addresses_or_coordinates():
    """Verify PromptBuilder hides sensitive physical addresses and GPS coordinates from AI prompt."""
    builder = PromptBuilder()
    secret_loc = SavedLocation(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        label="Home",
        address="99 Confidential Way, Secret Suite 400",
        latitude=12.34567,
        longitude=76.54321,
    )

    ai_req = builder.build(
        user_input="Book a cab from Home to Work",
        saved_locations=[secret_loc],
    )

    prompt_text = ai_req.messages[-1].content
    assert "- Home" in prompt_text
    assert "99 Confidential Way" not in prompt_text
    assert "12.34567" not in prompt_text
    assert "76.54321" not in prompt_text


# ============================================================================
# 16. Graph Traversal Visited Nodes Parity
# ============================================================================


@pytest.mark.asyncio
async def test_16_graph_traversal_visited_nodes_parity():
    """Verify exact visited_nodes path structure: clarification path vs completed quoting path."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    cp_manager = CheckpointManager(store=InMemoryCheckpointStore())
    mock_dispatcher = MagicMock()
    mock_dispatcher.dispatch = AsyncMock(
        return_value=MagicMock(success=True, data={"recommendation_id": uuid.uuid4()})
    )

    orchestrator = ChatGraphOrchestrator(
        provider=MockDeterministicAIProvider(),
        tool_dispatcher=mock_dispatcher,
        checkpoint_manager=cp_manager,
    )

    # 1. Incomplete slot request: Tool MUST NOT be visited
    res_incomplete = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id="sess_parity",
        message_text="Book me a cab",
        saved_locations=[mock_home, mock_work],
    )
    assert res_incomplete["visited_nodes"] == [
        "start",
        "intent",
        "decision",
        "llm",
        "memory",
        "response",
        "end",
    ]
    assert "tool" not in res_incomplete["visited_nodes"]

    # 2. Resolved slot request: Tool MUST be visited
    res_complete = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id="sess_parity",
        message_text="From Home to Work",
        saved_locations=[mock_home, mock_work],
    )
    assert res_complete["visited_nodes"] == [
        "start",
        "intent",
        "decision",
        "llm",
        "tool",
        "memory",
        "response",
        "end",
    ]
    assert "tool" in res_complete["visited_nodes"]


# ============================================================================
# 17. Multi-Turn State Retrieval Across Separate Service Instances
# ============================================================================


@pytest.mark.asyncio
async def test_17_multi_turn_checkpoint_restoration_across_chat_service_instances():
    """Verify separate ChatService instances share checkpoint store and restore multi-turn ride slots."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_multi_instances"
    mock_home, mock_work = _create_mock_saved_locations(user_id)

    # Create shared in-memory checkpoint store
    shared_store = InMemoryCheckpointStore()
    shared_cp_manager = CheckpointManager(store=shared_store)

    mock_dispatcher = MagicMock()
    mock_rec_id = uuid.uuid4()
    mock_dispatcher.dispatch = AsyncMock(
        return_value=MagicMock(success=True, data={"recommendation_id": mock_rec_id})
    )

    # Turn 1 with Instance A
    orchestrator_a = ChatGraphOrchestrator(
        provider=MockDeterministicAIProvider(),
        tool_dispatcher=mock_dispatcher,
        checkpoint_manager=shared_cp_manager,
    )
    turn1 = await orchestrator_a.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="I need a ride from Home",
        saved_locations=[mock_home, mock_work],
    )
    assert turn1["recommendation_id"] is None

    # Turn 2 with Instance B (fresh orchestrator instance using the same shared checkpoint manager)
    orchestrator_b = ChatGraphOrchestrator(
        provider=MockDeterministicAIProvider(),
        tool_dispatcher=mock_dispatcher,
        checkpoint_manager=shared_cp_manager,
    )
    turn2 = await orchestrator_b.execute_chat_turn(
        conversation_id=conv_id,
        user_id=user_id,
        session_id=session_id,
        message_text="To Work",
        saved_locations=[mock_home, mock_work],
    )

    assert turn2["recommendation_id"] == mock_rec_id
    ride = RideEntityState.model_validate(
        turn2["final_state"].memory.extracted_entities["ride"]
    )
    assert ride.status == RideSlotStatus.RESOLVED
    assert ride.pickup_point.saved_location_id == mock_home.id
    assert ride.destination_point.saved_location_id == mock_work.id
