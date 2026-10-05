import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.auth.auth_adapter import AuthAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.auth.keycloak")

try:
    import jwt
    import httpx
    KEYCLOAK_DEPS_AVAILABLE = True
except ImportError:
    jwt = None
    httpx = None
    KEYCLOAK_DEPS_AVAILABLE = False


class KeycloakAdapter(AuthAdapter):
    """Production Keycloak Identity Adapter for validating tokens against Keycloak realm endpoints."""

    def __init__(
        self,
        server_url: Optional[str] = None,
        realm: str = "master",
        connect_timeout: float = 5.0,
        request_timeout: float = 10.0,
    ) -> None:
        super().__init__(provider_id="auth.keycloak", name="Keycloak Identity Adapter", priority=80)
        self.server_url = server_url
        self.realm = realm
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._jwks_client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without network calls."""
        if context:
            self._context = context

        url = self._context.resolved_secrets.get("KEYCLOAK_URL", self.server_url)
        realm_name = self._context.resolved_secrets.get("KEYCLOAK_REALM", self.realm)
        self.server_url = url
        self.realm = realm_name

        if not KEYCLOAK_DEPS_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("KeycloakAdapter initialized without pyjwt/httpx dependencies.")
            return

        if not url:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("KeycloakAdapter initialized without KEYCLOAK_URL.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_jwks_client(self) -> Any:
        """Lazily instantiates PyJWKClient for Keycloak realm."""
        if not KEYCLOAK_DEPS_AVAILABLE:
            raise RuntimeError("pyjwt package is unavailable. Install 'pyjwt[crypto]' and 'httpx' to enable Keycloak adapter.")

        if self._jwks_client is None:
            if not self.server_url:
                raise ValueError("KEYCLOAK_URL missing from context secrets.")

            jwks_url = f"{self.server_url.rstrip('/')}/realms/{self.realm}/protocol/openid-connect/certs"

            def _init():
                return jwt.PyJWKClient(jwks_url, timeout=self.request_timeout)

            self._jwks_client = await asyncio.to_thread(_init)

        return self._jwks_client

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not KEYCLOAK_DEPS_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        if not self.server_url:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically resets JWKS client session."""
        self._jwks_client = None
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def authenticate_token(self, token: str) -> dict[str, Any]:
        """Validates Keycloak JWT token using realm JWKS."""
        jwks_client = await self._get_jwks_client()

        def _decode():
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
            payload["token_valid"] = True
            return payload

        return await asyncio.to_thread(_decode)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not KEYCLOAK_DEPS_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Keycloak",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "pyjwt/httpx package not installed"},
            )

        if not self.server_url:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Keycloak",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "KEYCLOAK_URL missing from secrets"},
            )

        latency = (time.perf_counter() - start_time) * 1000.0
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="Keycloak",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=IntegrationStatus.CONNECTED,
            latency_ms=round(latency, 2),
            details={"server_url": self.server_url, "realm": self.realm},
        )
