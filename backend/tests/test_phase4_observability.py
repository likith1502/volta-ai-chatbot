import pytest
from app.integrations.adapters.observability.prometheus_adapter import PrometheusObservabilityAdapter
from app.integrations.adapters.observability.opentelemetry_adapter import OpenTelemetryAdapter
from app.integrations.adapters.observability.grafana_adapter import GrafanaAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.status import IntegrationStatus


@pytest.mark.asyncio
async def test_observability_adapter_provider_ids_and_defaults():
    prom = PrometheusObservabilityAdapter()
    otel = OpenTelemetryAdapter()
    grafana = GrafanaAdapter()

    assert prom.provider_id == "observability.prometheus"
    assert otel.provider_id == "observability.opentelemetry"
    assert grafana.provider_id == "observability.grafana"


@pytest.mark.asyncio
async def test_initialization_safety_and_record_metric():
    prom = PrometheusObservabilityAdapter()
    await prom.initialize()
    await prom.record_metric("test_metric", 42.0)

    report = await prom.check_health()
    assert report.provider_id == "observability.prometheus"


@pytest.mark.asyncio
async def test_resource_cleanup_disconnect():
    prom = PrometheusObservabilityAdapter()
    await prom.disconnect()
    assert prom.status == IntegrationStatus.DISCONNECTED

    otel = OpenTelemetryAdapter()
    await otel.disconnect()
    assert otel.status == IntegrationStatus.DISCONNECTED
