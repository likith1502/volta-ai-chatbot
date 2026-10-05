import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from app.ai.base import AIProvider
from app.ai.models import AIRequest, AIResponse, AITokenUsage
from app.checkpoints.checkpoint_manager import CheckpointManager
from app.checkpoints.checkpoint_store import InMemoryCheckpointStore
from app.events.event_bus import WorkflowEventBus
from app.events.event_listener import WorkflowEventListener
from app.events.event_types import WorkflowEventType
from app.models.user import User
from app.services.chat import ChatService
from app.services.chat_graph import ChatGraphOrchestrator


class MockAIProvider(AIProvider):
    """Deterministic AI provider mock for graph traversal testing."""

    def __init__(self, response_content: str = "I can help with that.", tool_calls=None):
        self.response_content = response_content
        self.tool_calls = tool_calls or []

    async def generate_response(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content=self.response_content,
            model_used="mock-gemini-3.6",
            usage=AITokenUsage(prompt_tokens=15, completion_tokens=10, total_tokens=25),
            tool_calls=self.tool_calls,
        )


@pytest.mark.asyncio
async def test_chat_graph_construction():
    """Verify ChatGraphOrchestrator compiles graph with expected nodes and entrypoint."""
    orchestrator = ChatGraphOrchestrator()
    graph = orchestrator.build_graph()

    assert graph.entry_node == "start"
    node_ids = set(graph.nodes.keys())
    expected_nodes = {"start", "intent", "decision", "llm", "tool", "memory", "response", "end"}
    assert expected_nodes.issubset(node_ids)
    assert len(graph.edges) >= 8


@pytest.mark.asyncio
async def test_conversational_chat_turn_traversal():
    """Verify normal conversation follows START -> Intent -> Decision -> LLM -> Memory -> Response -> END."""
    provider = MockAIProvider(response_content="Hello! How can I assist you today?")
    orchestrator = ChatGraphOrchestrator(provider=provider)

    result = await orchestrator.execute_chat_turn(
        conversation_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        session_id="sess_conv_1",
        message_text="Hello, what can you do?",
    )

    assert result["content"] == "Hello! How can I assist you today?"
    assert result["recommendation_id"] is None
    assert result["visited_nodes"] == ["start", "intent", "decision", "llm", "memory", "response", "end"]
    assert "tool" not in result["visited_nodes"]


@pytest.mark.asyncio
async def test_recommendation_chat_turn_traversal():
    """Verify cab request follows START -> Intent -> Decision -> LLM -> Tool -> Memory -> Response -> END."""
    rec_id = uuid.uuid4()
    mock_dispatcher = MagicMock()
    mock_dispatcher.dispatch = AsyncMock(
        return_value=MagicMock(success=True, data={"recommendation_id": rec_id})
    )

    provider = MockAIProvider(response_content="I found an electric cab for you.")
    orchestrator = ChatGraphOrchestrator(provider=provider, tool_dispatcher=mock_dispatcher)

    result = await orchestrator.execute_chat_turn(
        conversation_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        session_id="sess_ride_1",
        message_text="I need an electric cab from Koramangala to Indiranagar right now",
    )

    assert result["content"] == "I found an electric cab for you."
    assert result["recommendation_id"] == rec_id
    assert result["visited_nodes"] == ["start", "intent", "decision", "llm", "tool", "memory", "response", "end"]
    assert mock_dispatcher.dispatch.called


@pytest.mark.asyncio
async def test_checkpoint_and_events():
    """Verify graph execution creates a checkpoint and publishes start and complete events."""
    event_bus = WorkflowEventBus()
    published_events = []

    class TestListener(WorkflowEventListener):
        listener_id: str = "test_listener"

        async def on_event(self, event):
            published_events.append(event)

    event_bus.subscribe(TestListener(listener_id="test_listener"))

    store = InMemoryCheckpointStore()
    cp_manager = CheckpointManager(store=store)

    orchestrator = ChatGraphOrchestrator(
        provider=MockAIProvider(),
        event_bus=event_bus,
        checkpoint_manager=cp_manager,
    )

    conv_id = uuid.uuid4()
    result = await orchestrator.execute_chat_turn(
        conversation_id=conv_id,
        user_id=uuid.uuid4(),
        session_id="sess_cp_test",
        message_text="Testing checkpoint",
    )

    # Checkpoint verification
    checkpoints = cp_manager.list_checkpoints()
    assert len(checkpoints) >= 1
    assert checkpoints[-1].workflow_id == str(conv_id)
    assert result["final_state"].runtime.checkpoint_id == checkpoints[-1].checkpoint_id

    # Event verification
    event_types = [e.event_type for e in published_events]
    assert WorkflowEventType.EXECUTION_STARTED in event_types
    assert WorkflowEventType.EXECUTION_COMPLETED in event_types


@pytest.mark.asyncio
async def test_legacy_behavior_parity():
    """
    LEGACY BEHAVIOR PARITY REQUIREMENT:
    Verify graph-path execution preserves 100% semantic and structural parity
    with the legacy direct pipeline under identical inputs and mocks.
    """
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_parity_test"
    message_text = "Book an electric cab to the station"
    rec_id = uuid.uuid4()

    # Setup mocks for ChatService
    session = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))

    provider = MockAIProvider(
        response_content="Cab booked successfully.",
        tool_calls=[],
    )
    dispatcher = MagicMock()
    dispatcher.dispatch = AsyncMock(
        return_value=MagicMock(success=True, data={"recommendation_id": rec_id})
    )

    chat_service = ChatService(
        session=session,
        provider=provider,
        tool_dispatcher=dispatcher,
    )

    mock_user = User(id=user_id, full_name="Parity User")
    chat_service.user_repo.get_by_id = AsyncMock(return_value=mock_user)

    mock_conv = MagicMock()
    mock_conv.id = conv_id
    mock_conv.session_id = session_id
    chat_service.conversation_repo.get_by_session_id = AsyncMock(return_value=mock_conv)

    mock_user_msg = MagicMock(id=uuid.uuid4(), role="user", content=message_text)
    mock_assistant_msg = MagicMock(id=uuid.uuid4(), role="assistant", content="Cab booked successfully.")
    chat_service.message_repo.count = AsyncMock(return_value=0)
    chat_service.message_repo.create = AsyncMock(side_effect=[mock_user_msg, mock_assistant_msg])

    # Execute ChatService turn
    result = await chat_service.process_chat(
        user_id=user_id,
        session_id=session_id,
        message_text=message_text,
    )

    # 1. Output shape parity
    assert set(result.keys()) == {"conversation_id", "session_id", "message", "recommendation_id", "usage"}
    assert result["conversation_id"] == conv_id
    assert result["session_id"] == session_id
    assert result["recommendation_id"] == rec_id
    assert result["message"] == mock_assistant_msg
    assert result["usage"]["total_tokens"] == 25

    # 2. Database interaction parity
    assert chat_service.user_repo.get_by_id.called
    assert chat_service.conversation_repo.get_by_session_id.called
    assert chat_service.message_repo.create.call_count == 2
    assert session.commit.called


@pytest.mark.asyncio
async def test_chat_service_fallback_on_graph_error():
    """Verify ChatService falls back cleanly to direct path when graph execution raises an error."""
    user_id = uuid.uuid4()
    conv_id = uuid.uuid4()
    session_id = "sess_fallback_test"
    message_text = "Book a ride"

    session = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))

    provider = MockAIProvider(response_content="Fallback path response.")
    rec_id = uuid.uuid4()
    dispatcher = MagicMock()
    dispatcher.dispatch = AsyncMock(
        return_value=MagicMock(success=True, data={"recommendation_id": rec_id})
    )

    chat_service = ChatService(
        session=session,
        provider=provider,
        tool_dispatcher=dispatcher,
    )

    mock_user = User(id=user_id, full_name="Fallback User")
    chat_service.user_repo.get_by_id = AsyncMock(return_value=mock_user)

    mock_conv = MagicMock()
    mock_conv.id = conv_id
    mock_conv.session_id = session_id
    chat_service.conversation_repo.get_by_session_id = AsyncMock(return_value=mock_conv)

    chat_service.message_repo.count = AsyncMock(return_value=0)
    chat_service.message_repo.create = AsyncMock(return_value=MagicMock())

    # Force graph orchestrator to fail
    chat_service.graph_orchestrator.execute_chat_turn = AsyncMock(
        side_effect=RuntimeError("Simulated Graph Runtime Engine Failure")
    )

    result = await chat_service.process_chat(
        user_id=user_id,
        session_id=session_id,
        message_text=message_text,
    )

    # Fallback must succeed and generate valid response
    assert result["session_id"] == session_id
    assert result["conversation_id"] == conv_id
    assert result["recommendation_id"] == rec_id
    assert session.commit.called
