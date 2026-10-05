import pytest
import uuid
from app.runtime.contracts import ChatMessage, RuntimeRequest
from app.runtime.exceptions import ProviderNotFoundError, RuntimeRetryExhaustedError
from app.runtime.execution_store import InMemoryExecutionStore
from app.runtime.factory import RuntimeFactory
from app.runtime.health import RuntimeHealthManager
from app.runtime.manager import RuntimeManager
from app.runtime.model_registry import ModelRegistry
from app.runtime.providers.gemini_provider import GeminiProvider
from app.runtime.providers.mock_provider import MockProvider
from app.runtime.registry import RuntimeRegistry
from app.runtime.serializer import ConversationSerializer


@pytest.mark.asyncio
async def test_mock_provider_generation():
    provider = MockProvider(latency_ms=1.0)
    await provider.initialize()

    req = RuntimeRequest(
        messages=[ChatMessage(role="user", content="Hello Volta!")],
        model="mock-model-v1",
    )

    res = await provider.generate(req)
    assert res.provider == "mock"
    assert "Volta" in res.content
    assert res.token_usage.total_tokens > 0
    assert provider.get_capabilities().supports_streaming is True


@pytest.mark.asyncio
async def test_mock_provider_streaming():
    provider = MockProvider(latency_ms=1.0)
    await provider.initialize()

    req = RuntimeRequest(
        messages=[ChatMessage(role="user", content="Test stream tokens")],
    )

    tokens = []
    async for msg in provider.generate_stream(req):
        tokens.append(msg.payload.get("token"))

    assert len(tokens) > 0


@pytest.mark.asyncio
async def test_runtime_registry():
    registry = RuntimeRegistry()
    mock_prov = MockProvider()
    registry.register(mock_prov)

    assert registry.exists("mock") is True
    assert registry.lookup("mock") == mock_prov
    assert "mock" in registry.list_providers()

    registry.register_factory("lazy_mock", lambda: MockProvider())
    assert registry.exists("lazy_mock") is True
    assert registry.lookup("lazy_mock").name == "mock"

    with pytest.raises(ProviderNotFoundError):
        registry.lookup("unknown_provider")


@pytest.mark.asyncio
async def test_runtime_factory():
    p1 = RuntimeFactory.create_provider("mock")
    assert isinstance(p1, MockProvider)

    p2 = RuntimeFactory.create_provider("gemini")
    assert isinstance(p2, GeminiProvider)


@pytest.mark.asyncio
async def test_runtime_health_manager():
    registry = RuntimeRegistry()
    registry.register(MockProvider())
    health_mgr = RuntimeHealthManager(registry)

    status = await health_mgr.check_provider_health("mock")
    assert status.is_healthy is True
    assert status.provider_name == "mock"

    all_statuses = await health_mgr.check_all_providers()
    assert "mock" in all_statuses


@pytest.mark.asyncio
async def test_runtime_manager_execution():
    manager = RuntimeManager()
    req = RuntimeRequest(
        messages=[ChatMessage(role="user", content="Test runtime manager")],
        provider="mock",
    )

    result = await manager.execute(req)
    assert result.execution_status == "COMPLETED"
    assert result.response is not None
    assert result.metrics.latency_ms > 0
    assert result.context.provider == "mock"
    assert result.runtime_version == "7.0.0"


@pytest.mark.asyncio
async def test_runtime_execution_store():
    store = InMemoryExecutionStore(capacity=10)
    manager = RuntimeManager(execution_store=store)

    req = RuntimeRequest(messages=[ChatMessage(role="user", content="Save store test")])
    result = await manager.execute(req)

    saved = await store.get_by_id(result.context.runtime_id)
    assert saved is not None
    assert saved.context.runtime_id == result.context.runtime_id

    recent = await store.list_recent(limit=5)
    assert len(recent) == 1


@pytest.mark.asyncio
async def test_model_registry():
    model_reg = ModelRegistry()
    m_info = model_reg.get_model("gemini-2.5-flash")
    assert m_info is not None
    assert m_info.provider_name == "gemini"

    gemini_models = model_reg.list_models(provider="gemini")
    assert len(gemini_models) >= 2


@pytest.mark.asyncio
async def test_conversation_serializer():
    manager = RuntimeManager()
    req = RuntimeRequest(messages=[ChatMessage(role="user", content="Serialize test")])
    result = await manager.execute(req)

    md_output = ConversationSerializer.to_markdown(req.messages, result)
    assert "# Runtime Turn Export" in md_output
    assert "Serialize test" in md_output

    json_output = ConversationSerializer.to_json(result)
    assert "COMPLETED" in json_output
