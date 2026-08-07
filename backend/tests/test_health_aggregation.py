import pytest
from app.integrations.health import IntegrationHealthManager
from app.integrations.registry import IntegrationRegistry
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.capabilities import IntegrationCapability
from app.integrations.adapters.storage.storage_adapter import FilesystemStorageAdapter
from app.integrations.adapters.storage.placeholders import S3StorageAdapter
from app.integrations.status import IntegrationStatus


@pytest.mark.asyncio
async def test_health_aggregation_all_green():
    """Validates aggregated platform health is GREEN when all adapters are healthy."""
    from app.integrations.factory import IntegrationFactory
    reg = IntegrationRegistry()
    for a in IntegrationFactory.create_reference_adapters():
        reg.register_provider(a)
    mgr = IntegrationHealthManager(reg)
    report = await mgr.check_platform_health()
    assert report.overall_health == HealthLevel.GREEN
    assert report.active_providers_count >= 8


@pytest.mark.asyncio
async def test_health_aggregation_single_yellow_upgrades_overall():
    """Validates that a YELLOW adapter causes overall health to be YELLOW."""
    from app.integrations.adapters.llm.llm_adapter import GeminiLLMAdapter
    from unittest.mock import AsyncMock, patch

    reg = IntegrationRegistry()
    fs = FilesystemStorageAdapter()
    await fs.initialize()
    reg.register_provider(fs)

    llm = GeminiLLMAdapter()
    await llm.initialize()

    # Patch check_health to return YELLOW report
    yellow_report = IntegrationHealthReport(
        provider_id="llm.gemini",
        provider_name="Google Gemini LLM Adapter",
        provider_type="Gemini",
        is_healthy=True,
        health_level=HealthLevel.YELLOW,
        status=IntegrationStatus.DEGRADED,
        latency_ms=250.0,
        error_rate=0.12,
    )
    with patch.object(llm, "check_health", new=AsyncMock(return_value=yellow_report)):
        reg.register_provider(llm)
        mgr = IntegrationHealthManager(reg)
        report = await mgr.check_platform_health()
    assert report.overall_health == HealthLevel.YELLOW


@pytest.mark.asyncio
async def test_health_aggregation_category_health_map_populated():
    """Validates that category_health map contains all registered adapter categories."""
    from app.integrations.factory import IntegrationFactory
    reg = IntegrationRegistry()
    for a in IntegrationFactory.create_reference_adapters():
        reg.register_provider(a)
    mgr = IntegrationHealthManager(reg)
    report = await mgr.check_platform_health()
    assert len(report.category_health) >= 8


@pytest.mark.asyncio
async def test_health_aggregation_provider_reports_all_have_latency():
    """Validates that every provider in health report has non-negative latency."""
    from app.integrations.factory import IntegrationFactory
    reg = IntegrationRegistry()
    for a in IntegrationFactory.create_reference_adapters():
        reg.register_provider(a)
    mgr = IntegrationHealthManager(reg)
    report = await mgr.check_platform_health()
    for rep in report.provider_reports:
        assert rep.latency_ms >= 0.0
