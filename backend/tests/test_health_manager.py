import pytest
from app.integrations.health import IntegrationHealthManager
from app.integrations.registry import IntegrationRegistry
from app.integrations.factory import IntegrationFactory
from app.integrations.health_level import HealthLevel


@pytest.mark.asyncio
async def test_health_manager_returns_aggregated_report():
    reg = IntegrationRegistry()
    for a in IntegrationFactory.create_reference_adapters():
        reg.register_provider(a)
    mgr = IntegrationHealthManager(reg)
    report = await mgr.check_platform_health()
    assert report.overall_health in [HealthLevel.GREEN, HealthLevel.YELLOW, HealthLevel.ORANGE, HealthLevel.RED]


@pytest.mark.asyncio
async def test_health_manager_counts_active_providers():
    reg = IntegrationRegistry()
    adapters = IntegrationFactory.create_reference_adapters()
    for a in adapters:
        reg.register_provider(a)
    mgr = IntegrationHealthManager(reg)
    report = await mgr.check_platform_health()
    assert report.active_providers_count == len(adapters)


@pytest.mark.asyncio
async def test_health_manager_returns_category_health_map():
    reg = IntegrationRegistry()
    for a in IntegrationFactory.create_reference_adapters():
        reg.register_provider(a)
    mgr = IntegrationHealthManager(reg)
    report = await mgr.check_platform_health()
    assert "storage" in report.category_health
    assert "llm" in report.category_health


@pytest.mark.asyncio
async def test_health_manager_single_provider():
    from app.integrations.adapters.storage.storage_adapter import FilesystemStorageAdapter
    reg = IntegrationRegistry()
    fs = FilesystemStorageAdapter()
    await fs.initialize()
    reg.register_provider(fs)
    mgr = IntegrationHealthManager(reg)
    report = await mgr.check_platform_health()
    assert report.active_providers_count == 1
    assert report.overall_health == HealthLevel.GREEN
