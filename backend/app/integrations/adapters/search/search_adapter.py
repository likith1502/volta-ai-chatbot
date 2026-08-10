from abc import ABC, abstractmethod
from typing import Any, Optional
from app.integrations.capabilities import IntegrationCapability
from app.integrations.provider import IntegrationProvider


class SearchAdapter(IntegrationProvider, ABC):
    """Abstract interface for enterprise full-text and semantic search engines."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name=name, category=IntegrationCapability.SEARCH, priority=priority)

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        pass


def __getattr__(name: str) -> Any:
    if name == "ElasticsearchSearchAdapter":
        from app.integrations.adapters.search.elasticsearch_adapter import ElasticsearchSearchAdapter
        return ElasticsearchSearchAdapter
    if name == "TypesenseSearchAdapter":
        from app.integrations.adapters.search.typesense_adapter import TypesenseSearchAdapter
        return TypesenseSearchAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "SearchAdapter",
    "ElasticsearchSearchAdapter",
    "TypesenseSearchAdapter",
]
