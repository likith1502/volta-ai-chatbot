import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.observability.observability_adapter import ObservabilityAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.observability.grafana")

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    httpx = None
    HTTPX_AVAILABLE = False


class GrafanaAdapter(ObservabilityAdapter):
    """Production Grafana Dashboard Adapter for pushing metrics and checking dashboard health."""

    def __init__(
        self,
        grafana_url: Optional[str] = None,
        connect_timeout: float = 5.0,
        request_timeout: float = 10.0,
    ) -> None:
        super().__init__(provider_id="observability.grafana", name="Grafana Dashboard Adapter", priority=70)
        self.grafana_url = grafana_url
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without network calls."""
        if context:
            self._context = context

        url = self._context.resolved_secrets.get("GRAFANA_URL", self.grafana_url)
        self.grafana_url = url

        if not HTTPX_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("GrafanaAdapter initialized without httpx dependency.")
            return

        if not url:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("GrafanaAdapter initialized without GRAFANA_URL.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_client(self) -> Any:
        """Lazily instantiates AsyncClient for Grafana API calls."""
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx package is unavailable. Install 'httpx' to enable Grafana dashboard adapter.")

        if self._client is None:
            api_key = self._context.resolved_secrets.get("GRAFANA_API_KEY", "")
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            self._client = httpx.AsyncClient(
                base_url=self.grafana_url,
                headers=headers,
                timeout=httpx.Timeout(self.request_timeout, connect=self.connect_timeout),
            )

        return self._client

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not HTTPX_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        if not self.grafana_url:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically closes httpx client session."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def record_metric(self, name: str, value: float, tags: Optional[dict[str, str]] = None) -> None:
        """Capability Honesty: Direct metric exposition push is handled via Prometheus endpoint."""
        logger.debug(f"Grafana metric '{name}'={value} logged for annotations.")

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check calling Grafana /api/health."""
        start_time = time.perf_counter()

        if not HTTPX_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Grafana",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "httpx package not installed"},
            )

        if not self.grafana_url:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Grafana",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "GRAFANA_URL missing from secrets"},
            )

        try:
            client = await self._get_client()
            res = await client.get("/api/health")
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Grafana",
                is_healthy=res.status_code == 200,
                health_level=HealthLevel.GREEN if res.status_code == 200 else HealthLevel.RED,
                status=IntegrationStatus.CONNECTED if res.status_code == 200 else IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"url": self.grafana_url, "status_code": res.status_code},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Grafana",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
