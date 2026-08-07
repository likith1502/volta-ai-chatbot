from abc import ABC, abstractmethod
from typing import Any, Optional
from app.integrations.capabilities import IntegrationCapability
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport, IntegrationProvider
from app.integrations.status import IntegrationStatus


class DatabaseAdapter(IntegrationProvider, ABC):
    """Abstract interface wrapping relational & key-value database repositories."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name=name, category=IntegrationCapability.DATABASE, priority=priority)

    @abstractmethod
    async def execute_query(self, query: str) -> Any:
        pass


class PostgresDatabaseAdapter(DatabaseAdapter):
    """Reference database adapter wrapping Async PostgreSQL connection pool."""

    def __init__(self) -> None:
        super().__init__(provider_id="database.postgres", name="PostgreSQL Async Database Adapter", priority=10)
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

    async def execute_query(self, query: str) -> Any:
        return [{"status": "success", "result": "mock_query_output"}]

    async def check_health(self) -> IntegrationHealthReport:
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="PostgreSQL",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=self.status,
            latency_ms=2.5,
        )


class RedisDatabaseAdapter(PostgresDatabaseAdapter):
    """Reference database adapter wrapping Redis key-value cache."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "database.redis"
        self._name = "Redis Cache & Key-Value Adapter"
        self._priority = 15
