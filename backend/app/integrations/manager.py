import logging
from typing import Any, Optional

from app.integrations.adapters.storage.storage_adapter import FilesystemStorageAdapter
from app.integrations.audit import IntegrationAuditLogger
from app.integrations.capabilities import IntegrationCapability
from app.integrations.config import IntegrationConfig
from app.integrations.contracts import (
    IntegrationConfigurePayload,
    IntegrationProviderRegisterPayload,
    IntegrationTestPayload,
)
from app.integrations.factory import IntegrationFactory
from app.integrations.health import AggregatedPlatformHealth, IntegrationHealthManager
from app.integrations.metrics import IntegrationMetrics
from app.integrations.provider import IntegrationHealthReport, IntegrationProvider
from app.integrations.registry import IntegrationRegistry
from app.integrations.secrets import EnvSecretProvider, SecretProvider
from app.integrations.statistics import IntegrationStatistics

logger = logging.getLogger("app.integrations.manager")


class IntegrationManager:
    """Central orchestration entry point for the Enterprise Integration Platform.

    Coordinates adapter registration, capability discovery, priority failovers, secret rotation, audit logging, and health aggregation.
    """

    def __init__(
        self,
        registry: Optional[IntegrationRegistry] = None,
        secret_provider: Optional[SecretProvider] = None,
        config: Optional[IntegrationConfig] = None,
    ) -> None:
        self.registry = registry or IntegrationRegistry()
        self.secret_provider = secret_provider or EnvSecretProvider()
        self.config = config or IntegrationConfig()
        self.audit_logger = IntegrationAuditLogger()

        self.health_manager = IntegrationHealthManager(self.registry)
        self.metrics = IntegrationMetrics()
        self.statistics = IntegrationStatistics()

        # Seed reference adapters into registry
        self._seed_reference_adapters()

    def _seed_reference_adapters(self) -> None:
        if not self.registry.list_providers():
            adapters = IntegrationFactory.create_reference_adapters()
            for a in adapters:
                self.registry.register_provider(a)
                self.audit_logger.log_event(
                    a.provider_id,
                    "Register",
                    {"name": a.name, "category": a.category.value},
                )

    async def register_provider(
        self, payload: IntegrationProviderRegisterPayload
    ) -> IntegrationProvider:
        """Registers a new provider dynamically."""
        adapter = FilesystemStorageAdapter(
            provider_id=payload.provider_id, priority=payload.priority
        )
        await adapter.initialize()
        self.registry.register_provider(adapter)
        self.audit_logger.log_event(
            payload.provider_id, "Register", payload.model_dump()
        )
        self.statistics.total_providers_registered += 1
        return adapter

    async def configure_provider(self, payload: IntegrationConfigurePayload) -> bool:
        """Configures options for an existing provider."""
        p = self.registry.get_provider(payload.provider_id)
        if not p:
            raise ValueError(f"Provider '{payload.provider_id}' not found.")
        self.audit_logger.log_event(
            payload.provider_id, "Configure", payload.model_dump()
        )
        return True

    async def test_provider_connection(
        self, payload: IntegrationTestPayload
    ) -> dict[str, Any]:
        """Tests live connectivity for a provider."""
        p = self.registry.get_provider(payload.provider_id)
        if not p:
            raise ValueError(f"Provider '{payload.provider_id}' not found.")
        report = await p.check_health()
        self.audit_logger.log_event(
            payload.provider_id, "ConnectionTest", {"is_healthy": report.is_healthy}
        )
        return report.model_dump()

    async def get_provider_health(self, provider_id: str) -> IntegrationHealthReport:
        """Returns health report for a specific provider."""
        p = self.registry.get_provider(provider_id)
        if not p:
            raise ValueError(f"Provider '{provider_id}' not found.")
        return await p.check_health()

    async def check_platform_health(self) -> AggregatedPlatformHealth:
        """Returns aggregated platform health report."""
        return await self.health_manager.check_platform_health()

    def get_provider(self, provider_id: str) -> Optional[IntegrationProvider]:
        return self.registry.get_provider(provider_id)

    def list_providers(
        self, category: Optional[IntegrationCapability] = None
    ) -> list[IntegrationProvider]:
        return self.registry.list_providers(category)

    def resolve_active_provider(
        self, category: IntegrationCapability
    ) -> Optional[IntegrationProvider]:
        """Resolves active provider with automatic priority failover."""
        return self.registry.resolve_active_provider(category)
