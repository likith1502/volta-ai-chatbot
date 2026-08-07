from abc import ABC, abstractmethod
from typing import Any, Optional
from app.integrations.capabilities import IntegrationCapability
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport, IntegrationProvider
from app.integrations.status import IntegrationStatus


class SearchAdapter(IntegrationProvider, ABC):
    """Abstract interface for full-text search engines."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name=name, category=IntegrationCapability.SEARCH, priority=priority)

    @abstractmethod
    async def search(self, query: str, index: str = "default") -> list[dict[str, Any]]:
        pass


class ElasticsearchSearchAdapter(SearchAdapter):
    """Extension placeholder for Elasticsearch / OpenSearch Adapter."""

    def __init__(self) -> None:
        super().__init__(provider_id="search.elasticsearch", name="Elasticsearch Engine Adapter", priority=10)
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

    async def search(self, query: str, index: str = "default") -> list[dict[str, Any]]:
        return [{"id": "doc_1", "score": 1.0, "title": f"Result for {query}"}]

    async def check_health(self) -> IntegrationHealthReport:
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="Elasticsearch",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=self.status,
            latency_ms=4.8,
        )


class TypesenseSearchAdapter(ElasticsearchSearchAdapter):
    """Extension placeholder for Typesense Search Engine Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "search.typesense"
        self._name = "Typesense Search Adapter"
