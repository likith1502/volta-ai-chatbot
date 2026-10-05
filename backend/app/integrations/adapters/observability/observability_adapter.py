from abc import ABC, abstractmethod
from typing import Any, Optional
from app.integrations.capabilities import IntegrationCapability
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport, IntegrationProvider
from app.integrations.status import IntegrationStatus


class ObservabilityAdapter(IntegrationProvider, ABC):
    """Abstract interface for metrics, tracing, and log observability exporters."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name=name, category=IntegrationCapability.OBSERVABILITY, priority=priority)

    @abstractmethod
    async def record_metric(self, name: str, value: float, tags: Optional[dict[str, str]] = None) -> None:
        pass


class SentryAdapter(ObservabilityAdapter):
    """Sentry Error Monitoring Adapter."""

    def __init__(self) -> None:
        super().__init__(provider_id="observability.sentry", name="Sentry Error Monitoring Adapter", priority=60)
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[Any] = None) -> None:
        self._status = IntegrationStatus.READY
        await self.connect()

    async def connect(self) -> bool:
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def record_metric(self, name: str, value: float, tags: Optional[dict[str, str]] = None) -> None:
        pass

    async def check_health(self) -> IntegrationHealthReport:
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="Sentry",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=self.status,
            latency_ms=1.2,
        )


def __getattr__(name: str) -> Any:
    if name == "PrometheusObservabilityAdapter":
        from app.integrations.adapters.observability.prometheus_adapter import PrometheusObservabilityAdapter
        return PrometheusObservabilityAdapter
    if name == "OpenTelemetryAdapter":
        from app.integrations.adapters.observability.opentelemetry_adapter import OpenTelemetryAdapter
        return OpenTelemetryAdapter
    if name == "GrafanaAdapter":
        from app.integrations.adapters.observability.grafana_adapter import GrafanaAdapter
        return GrafanaAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ObservabilityAdapter",
    "PrometheusObservabilityAdapter",
    "OpenTelemetryAdapter",
    "GrafanaAdapter",
    "SentryAdapter",
]
