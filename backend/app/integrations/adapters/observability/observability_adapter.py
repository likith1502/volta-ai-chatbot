from abc import ABC, abstractmethod
from typing import Any, Optional

from app.integrations.capabilities import IntegrationCapability
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport, IntegrationProvider
from app.integrations.status import IntegrationStatus


class ObservabilityAdapter(IntegrationProvider, ABC):
    """Abstract interface for metrics, tracing, and log observability exporters."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(
            provider_id=provider_id,
            name=name,
            category=IntegrationCapability.OBSERVABILITY,
            priority=priority,
        )

    @abstractmethod
    async def record_metric(
        self, name: str, value: float, tags: Optional[dict[str, str]] = None
    ) -> None:
        pass


class PrometheusObservabilityAdapter(ObservabilityAdapter):
    """Reference observability adapter exporting Prometheus metrics."""

    def __init__(self) -> None:
        super().__init__(
            provider_id="observability.prometheus",
            name="Prometheus Observability Adapter",
            priority=10,
        )
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

    async def record_metric(
        self, name: str, value: float, tags: Optional[dict[str, str]] = None
    ) -> None:
        pass

    async def check_health(self) -> IntegrationHealthReport:
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="Prometheus",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=self.status,
            latency_ms=0.4,
        )


class OpenTelemetryAdapter(PrometheusObservabilityAdapter):
    """Extension placeholder for OpenTelemetry Tracing Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "observability.opentelemetry"
        self._name = "OpenTelemetry Collector Adapter"


class SentryAdapter(PrometheusObservabilityAdapter):
    """Extension placeholder for Sentry Error Tracking Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "observability.sentry"
        self._name = "Sentry Error Monitoring Adapter"
