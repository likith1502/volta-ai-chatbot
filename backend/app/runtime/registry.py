import logging
from typing import Callable, Optional
from app.runtime.base import RuntimeProvider
from app.runtime.exceptions import ProviderNotFoundError

logger = logging.getLogger("app.runtime.registry")


class RuntimeRegistry:
    """Thread-safe provider registry managing available RuntimeProvider implementations and factory initializers."""

    def __init__(self) -> None:
        self._providers: dict[str, RuntimeProvider] = {}
        self._factories: dict[str, Callable[[], RuntimeProvider]] = {}

    def register(self, provider: RuntimeProvider) -> None:
        """Registers a concrete RuntimeProvider instance."""
        name = provider.name.lower()
        self._providers[name] = provider
        logger.info(f"Registered RuntimeProvider '{name}'")

    def register_factory(self, provider_name: str, factory: Callable[[], RuntimeProvider]) -> None:
        """Registers a factory function for lazy provider construction."""
        name = provider_name.lower()
        self._factories[name] = factory
        logger.info(f"Registered lazy factory for provider '{name}'")

    def unregister(self, provider_name: str) -> None:
        """Unregisters a provider or factory."""
        name = provider_name.lower()
        self._providers.pop(name, None)
        self._factories.pop(name, None)

    def lookup(self, provider_name: str) -> RuntimeProvider:
        """Retrieves registered provider or raises ProviderNotFoundError."""
        name = provider_name.lower()
        if name in self._providers:
            return self._providers[name]

        if name in self._factories:
            provider = self._factories[name]()
            self._providers[name] = provider
            return provider

        raise ProviderNotFoundError(f"Provider '{provider_name}' is not registered in RuntimeRegistry.")

    def get(self, provider_name: str) -> Optional[RuntimeProvider]:
        """Safely retrieves provider instance if present, else returns None."""
        try:
            return self.lookup(provider_name)
        except ProviderNotFoundError:
            return None

    def exists(self, provider_name: str) -> bool:
        """Returns True if provider instance or factory is registered."""
        name = provider_name.lower()
        return name in self._providers or name in self._factories

    def list_providers(self) -> list[str]:
        """Returns list of all registered provider names."""
        keys = set(self._providers.keys()).union(set(self._factories.keys()))
        return list(sorted(keys))
