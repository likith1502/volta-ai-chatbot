import pytest
from app.integrations.manager import IntegrationManager
from app.integrations.capabilities import IntegrationCapability
from app.integrations.status import IntegrationStatus
from app.integrations.health_level import HealthLevel
from app.integrations.contracts import IntegrationTestPayload, IntegrationConfigurePayload


@pytest.mark.asyncio
async def test_integration_manager_initializes_with_reference_adapters():
    mgr = IntegrationManager()
    providers = mgr.list_providers()
    assert len(providers) >= 8


@pytest.mark.asyncio
async def test_integration_manager_lists_by_category():
    mgr = IntegrationManager()
    storage = mgr.list_providers(IntegrationCapability.STORAGE)
    assert len(storage) >= 1
    assert all(p.category == IntegrationCapability.STORAGE for p in storage)


@pytest.mark.asyncio
async def test_integration_manager_resolve_active_provider():
    mgr = IntegrationManager()
    p = mgr.resolve_active_provider(IntegrationCapability.LLM)
    assert p is not None
    assert p.category == IntegrationCapability.LLM


@pytest.mark.asyncio
async def test_integration_manager_test_provider_connection():
    mgr = IntegrationManager()
    payload = IntegrationTestPayload(provider_id="storage.filesystem")
    result = await mgr.test_provider_connection(payload)
    assert isinstance(result, dict)
    assert "is_healthy" in result


@pytest.mark.asyncio
async def test_integration_manager_configure_provider():
    mgr = IntegrationManager()
    payload = IntegrationConfigurePayload(provider_id="storage.filesystem", options={"root_dir": "./data"})
    result = await mgr.configure_provider(payload)
    assert result is True


@pytest.mark.asyncio
async def test_integration_manager_get_provider_by_id():
    mgr = IntegrationManager()
    p = mgr.get_provider("storage.filesystem")
    assert p is not None
    assert p.provider_id == "storage.filesystem"


@pytest.mark.asyncio
async def test_integration_manager_get_platform_health():
    mgr = IntegrationManager()
    health = await mgr.check_platform_health()
    assert health.overall_health in [HealthLevel.GREEN, HealthLevel.YELLOW, HealthLevel.ORANGE, HealthLevel.RED]
    assert health.active_providers_count >= 1
