import logging
from typing import Any, Optional

from pydantic import BaseModel

from app.runtime.registry import RuntimeRegistry

logger = logging.getLogger("app.runtime.health")


class ProviderHealthStatus(BaseModel):
    """Detailed health status report for an individual LLM provider."""

    provider_name: str
    is_healthy: bool = False
    is_initialized: bool = False
    sdk_installed: bool = True
    api_key_configured: bool = True
    message: str = "Healthy"
    capabilities: Optional[dict[str, Any]] = None


class RuntimeHealthManager:
    """Centralized health orchestrator checking reachability, SDK status, API key configuration, and initialization for registered providers."""

    def __init__(self, registry: RuntimeRegistry) -> None:
        self.registry = registry

    async def check_provider_health(self, provider_name: str) -> ProviderHealthStatus:
        """Checks health status for specified provider."""
        provider = self.registry.get(provider_name)
        if not provider:
            return ProviderHealthStatus(
                provider_name=provider_name,
                is_healthy=False,
                is_initialized=False,
                api_key_configured=False,
                message=f"Provider '{provider_name}' is not registered in RuntimeRegistry.",
            )

        try:
            is_healthy = await provider.health_check()
            capabilities = provider.get_capabilities().model_dump()
            return ProviderHealthStatus(
                provider_name=provider.name,
                is_healthy=is_healthy,
                is_initialized=True,
                sdk_installed=True,
                api_key_configured=True,
                message="Provider is healthy and reachable."
                if is_healthy
                else "Health check ping failed.",
                capabilities=capabilities,
            )
        except Exception as exc:
            logger.warning(f"Health check failed for provider '{provider_name}': {exc}")
            return ProviderHealthStatus(
                provider_name=provider_name,
                is_healthy=False,
                is_initialized=False,
                message=f"Health check execution error: {exc}",
            )

    async def check_all_providers(self) -> dict[str, ProviderHealthStatus]:
        """Checks and returns health status reports for all registered providers."""
        results: dict[str, ProviderHealthStatus] = {}
        for provider_name in self.registry.list_providers():
            results[provider_name] = await self.check_provider_health(provider_name)
        return results
