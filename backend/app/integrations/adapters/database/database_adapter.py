from abc import ABC, abstractmethod
from typing import Any
from app.integrations.capabilities import IntegrationCapability
from app.integrations.provider import IntegrationProvider


class DatabaseAdapter(IntegrationProvider, ABC):
    """Abstract interface wrapping relational & key-value database repositories."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name=name, category=IntegrationCapability.DATABASE, priority=priority)

    @abstractmethod
    async def execute_query(self, query: str) -> Any:
        pass


def __getattr__(name: str) -> Any:
    if name == "PostgresDatabaseAdapter":
        from app.integrations.adapters.database.postgres_adapter import PostgresDatabaseAdapter
        return PostgresDatabaseAdapter
    if name == "RedisDatabaseAdapter":
        from app.integrations.adapters.database.redis_adapter import RedisDatabaseAdapter
        return RedisDatabaseAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DatabaseAdapter",
    "PostgresDatabaseAdapter",
    "RedisDatabaseAdapter",
]
