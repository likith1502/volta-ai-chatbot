import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.auth.auth_adapter import AuthAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.auth.oauth2")

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    httpx = None
    HTTPX_AVAILABLE = False


class OAuth2AuthAdapter(AuthAdapter):
    """Production OAuth2 Authentication Adapter performing token introspection and validation."""

    def __init__(
        self,
        introspection_endpoint: Optional[str] = None,
        connect_timeout: float = 5.0,
        request_timeout: float = 10.0,
    ) -> None:
        super().__init__(provider_id="auth.oauth2", name="OAuth2 Authentication Adapter", priority=85)
        self.introspection_endpoint = introspection_endpoint
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without making network calls."""
        if context:
            self._context = context

        endpoint = self._context.resolved_secrets.get("OAUTH2_INTROSPECTION_URL", self.introspection_endpoint)
        self.introspection_endpoint = endpoint

        if not HTTPX_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("OAuth2AuthAdapter initialized without httpx dependency.")
            return

        if not endpoint:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("OAuth2AuthAdapter initialized without introspection endpoint.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_client(self) -> Any:
        """Lazily instantiates AsyncClient for OAuth2 introspection calls."""
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx package is unavailable. Install 'httpx' to enable OAuth2 authentication.")

        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.request_timeout, connect=self.connect_timeout),
            )

        return self._client

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not HTTPX_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        if not self.introspection_endpoint:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically closes HTTP client session."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def authenticate_token(self, token: str) -> dict[str, Any]:
        """Validates OAuth2 bearer token against introspection endpoint."""
        if not self.introspection_endpoint:
            # Capability Honesty: return unconfigured state without hard-coded fake validation
            return {"active": False, "error": "unsupported_operation", "message": "Introspection endpoint not configured"}

        client = await self._get_client()
        client_id = self._context.resolved_secrets.get("OAUTH2_CLIENT_ID", "")
        client_secret = self._context.resolved_secrets.get("OAUTH2_CLIENT_SECRET", "")

        res = await client.post(
            self.introspection_endpoint,
            data={"token": token},
            auth=(client_id, client_secret) if client_id else None,
        )
        res.raise_for_status()
        return res.json()

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not HTTPX_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="OAuth2",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "httpx package not installed"},
            )

        if not self.introspection_endpoint:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="OAuth2",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "OAUTH2_INTROSPECTION_URL missing from secrets"},
            )

        latency = (time.perf_counter() - start_time) * 1000.0
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="OAuth2",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=IntegrationStatus.CONNECTED,
            latency_ms=round(latency, 2),
            details={"endpoint": self.introspection_endpoint},
        )
