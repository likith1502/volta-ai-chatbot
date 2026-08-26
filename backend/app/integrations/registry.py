import logging
from typing import Optional

from app.integrations.capabilities import IntegrationCapability
from app.integrations.provider import IntegrationProvider
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.registry")


class IntegrationRegistry:
    """Registry maintaining active production integration adapters with capability filtering & automatic failover."""

    def __init__(self) -> None:
        self._providers: dict[str, IntegrationProvider] = {}

    def register_provider(self, provider: IntegrationProvider) -> None:
        self._providers[provider.provider_id] = provider
        logger.info(
            f"IntegrationRegistry registered provider '{provider.provider_id}' ({provider.name}) with priority {provider.priority}"
        )

    def get_provider(self, provider_id: str) -> Optional[IntegrationProvider]:
        return self._providers.get(provider_id)

    def list_providers(
        self, category: Optional[IntegrationCapability] = None
    ) -> list[IntegrationProvider]:
        if category:
            return [p for p in self._providers.values() if p.category == category]
        return list(self._providers.values())

    def find_by_capability(
        self, category: IntegrationCapability
    ) -> list[IntegrationProvider]:
        """Finds providers by capability category sorted by priority (highest priority first for failover)."""
        matches = [p for p in self._providers.values() if p.category == category]
        matches.sort(key=lambda p: p.priority, reverse=True)
        return matches

    def resolve_active_provider(
        self, category: IntegrationCapability
    ) -> Optional[IntegrationProvider]:
        """Resolves highest priority healthy/connected provider in a capability category for automatic failover."""
        candidates = self.find_by_capability(category)
        for p in candidates:
            if p.status in [
                IntegrationStatus.CONNECTED,
                IntegrationStatus.READY,
                IntegrationStatus.CONFIGURED,
            ]:
                return p
        return candidates[0] if candidates else None
