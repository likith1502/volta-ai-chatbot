from abc import ABC, abstractmethod

from app.integrations.provider import IntegrationProvider


class BeforeProviderConnectHook(ABC):
    @abstractmethod
    async def before_connect(self, provider: IntegrationProvider) -> None:
        pass


class AfterProviderFailoverHook(ABC):
    @abstractmethod
    async def after_failover(
        self, category: str, active_provider: IntegrationProvider
    ) -> None:
        pass
