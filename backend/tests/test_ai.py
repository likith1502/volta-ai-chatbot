import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.ai.base import AIProvider
from app.ai.exceptions import AIProviderException
from app.ai.factory import AIProviderFactory
from app.ai.memory.factory import MemoryStrategyFactory
from app.ai.memory.recent import RecentConversationStrategy
from app.ai.models import AIMessage, AIRequest, AIResponse, AITokenUsage, AIToolCall
from app.ai.prompts.prompt_builder import PromptBuilder
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.tools.dispatcher import AIToolDispatcher
from app.ai.tools.recommendation_tool import RecommendationTool
from app.ai.tools.registry import AIToolRegistry
from app.api.dependencies.services import get_chat_service
from app.main import app
from app.models.memory import Memory
from app.models.message import Message
from app.models.user import User
from app.services.chat import ChatService

client = TestClient(app)


class MockAIProvider(AIProvider):
    """Deterministic mock provider for unit and integration testing."""

    async def generate_response(self, request: AIRequest) -> AIResponse:
        return AIResponse(
            content="I can help you book a sedan to the airport.",
            role="assistant",
            model_used="gpt-4o-mini-mock",
            finish_reason="stop",
            usage=AITokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
        )


def test_ai_provider_factory_and_openai_provider():
    """Verify AIProviderFactory and OpenAIProvider fallback response."""
    provider = AIProviderFactory.get_provider("openai")
    assert isinstance(provider, OpenAIProvider)

    with pytest.raises(AIProviderException):
        AIProviderFactory.get_provider("unknown_provider")


@pytest.mark.asyncio
async def test_memory_strategy_factory_and_recent_strategy():
    """Verify MemoryStrategyFactory and RecentConversationStrategy execution."""
    strategy = MemoryStrategyFactory.get_strategy("recent")
    assert isinstance(strategy, RecentConversationStrategy)

    with pytest.raises(AIProviderException):
        MemoryStrategyFactory.get_strategy("unknown_strategy")

    session = AsyncMock()
    mock_res = MagicMock()
    mock_scalars = MagicMock()
    mock_mem = Memory(id=uuid.uuid4(), memory_key="fav_dest", memory_value="Airport")
    mock_scalars.all.return_value = [mock_mem]
    mock_res.scalars.return_value = mock_scalars
    session.execute = AsyncMock(return_value=mock_res)

    memories = await strategy.retrieve_memories(session, uuid.uuid4())
    assert len(memories) == 1
    assert memories[0].memory_key == "fav_dest"


def test_prompt_builder():
    """Verify PromptBuilder merges system prompt, history, memories, and user input."""
    builder = PromptBuilder(system_prompt="Test System Prompt")
    msg1 = Message(role="user", content="Hi")
    msg2 = Message(role="assistant", content="Hello")
    mem = Memory(memory_key="preferred_ride", memory_value="Sedan")

    ai_req = builder.build(
        user_input="Book a sedan",
        conversation_history=[msg1, msg2],
        memories=[mem],
    )

    assert ai_req.system_prompt == "Test System Prompt"
    assert len(ai_req.messages) == 3
    assert "[User Context & Preferences]" in ai_req.messages[-1].content


@pytest.mark.asyncio
async def test_tool_registry_and_dispatcher():
    """Verify AIToolRegistry, RecommendationTool, and AIToolDispatcher."""
    session = AsyncMock()
    tool = RecommendationTool(session)

    registry = AIToolRegistry()
    registry.register(tool)
    assert registry.get("recommendation") == tool

    dispatcher = AIToolDispatcher(registry)

    # Mock recommendation service call inside tool
    tool.recommendation_service.create_recommendation = AsyncMock(
        return_value=MagicMock(id=uuid.uuid4(), status=MagicMock(value="pending"), recommendation_type="ride")
    )

    call = AIToolCall(
        tool_name="recommendation",
        arguments={"conversation_id": str(uuid.uuid4()), "user_query": "Need a ride"},
    )
    result = await dispatcher.dispatch(call)

    assert result.success is True
    assert result.tool_name == "recommendation"
    assert "recommendation_id" in result.data


@pytest.mark.asyncio
async def test_chat_service_orchestration_with_tools_and_memory():
    """Verify ChatService orchestrates memory strategy, prompt builder, AI provider, and tool dispatcher."""
    session = AsyncMock()
    session.add = MagicMock()

    # Mock DB query result for history fetching
    mock_execute_res = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_execute_res.scalars.return_value = mock_scalars
    session.execute = AsyncMock(return_value=mock_execute_res)

    mock_provider = MockAIProvider()
    chat_service = ChatService(session=session, provider=mock_provider)

    user_id = uuid.uuid4()
    mock_user = User(id=user_id, full_name="Chat User")
    chat_service.user_repo.get_by_id = AsyncMock(return_value=mock_user)
    chat_service.conversation_repo.get_by_session_id = AsyncMock(return_value=None)

    mock_conv = MagicMock()
    mock_conv.id = uuid.uuid4()
    mock_conv.session_id = "sess_ai_test"
    chat_service.conversation_repo.create = AsyncMock(return_value=mock_conv)

    mock_msg = MagicMock()
    mock_msg.role = "assistant"
    mock_msg.content = "I can help you book a sedan to the airport."
    chat_service.message_repo.create = AsyncMock(return_value=mock_msg)
    chat_service.message_repo.count = AsyncMock(return_value=0)

    # Mock Tool Dispatcher execution
    mock_rec_id = uuid.uuid4()
    chat_service.tool_dispatcher.dispatch = AsyncMock(
        return_value=MagicMock(success=True, data={"recommendation_id": mock_rec_id})
    )

    # Execute Chat Processing for Ride Request
    result = await chat_service.process_chat(
        user_id=user_id,
        session_id="sess_ai_test",
        message_text="Book a ride to the airport",
    )

    assert result["session_id"] == "sess_ai_test"
    assert result["recommendation_id"] == mock_rec_id  # Tool execution dispatched!
    assert result["usage"]["total_tokens"] == 30
    assert session.commit.called


def test_post_chat_api_endpoint():
    """Verify POST /api/v1/chat endpoint serialization and dependency overrides."""
    mock_chat_service = MagicMock()
    conv_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_msg_data = {
        "role": "assistant",
        "content": "Ride recommendation generated.",
        "model_used": "gpt-4o-mini-mock",
        "token_count": 30,
    }

    mock_response = {
        "conversation_id": conv_id,
        "session_id": "sess_api_chat",
        "message": mock_msg_data,
        "recommendation_id": uuid.uuid4(),
        "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
    }

    mock_chat_service.process_chat = AsyncMock(return_value=mock_response)
    app.dependency_overrides[get_chat_service] = lambda: mock_chat_service

    res = client.post(
        "/api/v1/chat",
        json={
            "user_id": str(user_id),
            "session_id": "sess_api_chat",
            "message": "I need a ride to the station",
        },
    )

    assert res.status_code == 200
    payload = res.json()
    assert payload["success"] is True
    assert payload["data"]["session_id"] == "sess_api_chat"
    assert payload["data"]["message"]["role"] == "assistant"
    assert payload["data"]["recommendation_id"] is not None

    app.dependency_overrides.clear()
