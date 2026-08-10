import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.auth.auth_adapter import AuthAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.auth.auth0")

try:
    import jwt
    import httpx
    AUTH0_DEPS_AVAILABLE = True
except ImportError:
    jwt = None
    httpx = None
    AUTH0_DEPS_AVAILABLE = False


class Auth0Adapter(AuthAdapter):
    """Production Auth0 Authentication Adapter for validating JWT tokens against Auth0 JWKS."""

    def __init__(
        self,
        domain: Optional[str] = None,
        audience: Optional[str] = None,
        connect_timeout: float = 5.0,
        request_timeout: float = 10.0,
    ) -> None:
        super().__init__(provider_id="auth.auth0", name="Auth0 Authentication Adapter", priority=90)
        self.domain = domain
        self.audience = audience
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._jwks_client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without network calls."""
        if context:
            self._context = context

        dom = self._context.resolved_secrets.get("AUTH0_DOMAIN", self.domain)
        aud = self._context.resolved_secrets.get("AUTH0_AUDIENCE", self.audience)
        self.domain = dom
        self.audience = aud

        if not AUTH0_DEPS_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("Auth0Adapter initialized without pyjwt/httpx dependencies.")
            return

        if not dom:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("Auth0Adapter initialized without AUTH0_DOMAIN.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_jwks_client(self) -> Any:
        """Lazily instantiates PyJWKClient for Auth0 domain."""
        if not AUTH0_DEPS_AVAILABLE:
            raise RuntimeError("pyjwt package is unavailable. Install 'pyjwt[crypto]' and 'httpx' to enable Auth0 adapter.")

        if self._jwks_client is None:
            if not self.domain:
                raise ValueError("AUTH0_DOMAIN missing from context secrets.")

            jwks_url = f"https://{self.domain}/.well-known/jwks.json"

            def _init():
                return jwt.PyJWKClient(jwks_url, timeout=self.request_timeout)

            self._jwks_client = await asyncio.to_thread(_init)

        return self._jwks_client

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not AUTH0_DEPS_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        if not self.domain:
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
        """Validates Auth0 JWT token using JWKS public keys."""
        jwks_client = await self._get_jwks_client()

        def _decode():
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=f"https://{self.domain}/",
            )
            payload["token_valid"] = True
            return payload

        return await asyncio.to_thread(_decode)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not AUTH0_DEPS_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Auth0",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "pyjwt/httpx package not installed"},
            )

        if not self.domain:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Auth0",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "AUTH0_DOMAIN missing from secrets"},
            )

        latency = (time.perf_counter() - start_time) * 1000.0
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="Auth0",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=IntegrationStatus.CONNECTED,
            latency_ms=round(latency, 2),
            details={"domain": self.domain, "audience": self.audience},
        )
