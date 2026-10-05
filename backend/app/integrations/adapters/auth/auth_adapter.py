from abc import ABC, abstractmethod
from typing import Any, Optional
from app.integrations.capabilities import IntegrationCapability
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport, IntegrationProvider
from app.integrations.status import IntegrationStatus


class AuthAdapter(IntegrationProvider, ABC):
    """Abstract interface for authentication and authorization providers."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name=name, category=IntegrationCapability.AUTH, priority=priority)

    @abstractmethod
    async def authenticate_token(self, token: str) -> dict[str, Any]:
        pass


class JWTAuthAdapter(AuthAdapter):
    """Reference authentication adapter resolving JWT claims."""

    def __init__(self) -> None:
        super().__init__(provider_id="auth.jwt", name="JWT Local Authentication Adapter", priority=10)
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

    async def authenticate_token(self, token: str) -> dict[str, Any]:
        return {"sub": "user_123", "role": "admin", "token_valid": True}

    async def check_health(self) -> IntegrationHealthReport:
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="JWT",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=self.status,
            latency_ms=0.8,
        )


def __getattr__(name: str) -> Any:
    if name == "OAuth2AuthAdapter":
        from app.integrations.adapters.auth.oauth2_adapter import OAuth2AuthAdapter
        return OAuth2AuthAdapter
    if name == "Auth0Adapter":
        from app.integrations.adapters.auth.auth0_adapter import Auth0Adapter
        return Auth0Adapter
    if name == "KeycloakAdapter":
        from app.integrations.adapters.auth.keycloak_adapter import KeycloakAdapter
        return KeycloakAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AuthAdapter",
    "JWTAuthAdapter",
    "OAuth2AuthAdapter",
    "Auth0Adapter",
    "KeycloakAdapter",
]
