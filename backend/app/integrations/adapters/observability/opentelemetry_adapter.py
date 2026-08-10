import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.observability.observability_adapter import ObservabilityAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.observability.opentelemetry")

try:
    from opentelemetry import trace
    from opentelemetry.trace import Tracer
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    trace = None
    Tracer = None
    OPENTELEMETRY_AVAILABLE = False


class OpenTelemetryAdapter(ObservabilityAdapter):
    """Production OpenTelemetry Collector Adapter using opentelemetry-sdk with lazy loading."""

    def __init__(self, service_name: str = "volta-ai-chatbot") -> None:
        super().__init__(provider_id="observability.opentelemetry", name="OpenTelemetry Collector Adapter", priority=85)
        self.service_name = service_name
        self._tracer: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without network calls."""
        if context:
            self._context = context

        name = self._context.resolved_secrets.get("OTEL_SERVICE_NAME", self.service_name)
        self.service_name = name

        if not OPENTELEMETRY_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("OpenTelemetryAdapter initialized without opentelemetry dependency.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_tracer(self) -> Any:
        """Lazily obtains OpenTelemetry tracer instance."""
        if not OPENTELEMETRY_AVAILABLE:
            raise RuntimeError("opentelemetry package is unavailable. Install 'opentelemetry-api' to enable OpenTelemetry exporter.")

        if self._tracer is None:
            def _init():
                return trace.get_tracer(self.service_name)

            self._tracer = await asyncio.to_thread(_init)

        return self._tracer

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not OPENTELEMETRY_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically resets OpenTelemetry tracer session."""
        self._tracer = None
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def record_metric(self, name: str, value: float, tags: Optional[dict[str, str]] = None) -> None:
        """Records metric/trace event using OpenTelemetry tracer."""
        if not OPENTELEMETRY_AVAILABLE:
            return

        tracer = await self._get_tracer()

        def _record():
            with tracer.start_as_current_span(name) as span:
                span.set_attribute("metric.value", value)
                if tags:
                    for k, v in tags.items():
                        span.set_attribute(f"tag.{k}", v)

        await asyncio.to_thread(_record)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not OPENTELEMETRY_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="OpenTelemetry",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "opentelemetry package not installed"},
            )

        latency = (time.perf_counter() - start_time) * 1000.0
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="OpenTelemetry",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=IntegrationStatus.CONNECTED,
            latency_ms=round(latency, 2),
            details={"service_name": self.service_name},
        )
