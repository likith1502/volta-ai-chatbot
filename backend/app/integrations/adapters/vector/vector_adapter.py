from abc import ABC, abstractmethod
from typing import Any, Optional
from app.integrations.capabilities import IntegrationCapability
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport, IntegrationProvider
from app.integrations.status import IntegrationStatus


class VectorDatabaseAdapter(IntegrationProvider, ABC):
    """Abstract interface wrapping vector store repositories."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name=name, category=IntegrationCapability.VECTOR, priority=priority)

    @abstractmethod
    async def upsert_vector(self, vector_id: str, vector: list[float], metadata: dict[str, Any]) -> bool:
        pass

    @abstractmethod
    async def query_vector(self, query_vector: list[float], top_k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        pass


class InMemoryVectorAdapter(VectorDatabaseAdapter):
    """Reference vector database adapter storing vectors in memory."""

    def __init__(self) -> None:
        super().__init__(provider_id="vector.inmemory", name="In-Memory Vector DB Adapter", priority=10)
        self._vectors: dict[str, tuple[list[float], dict[str, Any]]] = {}
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

    async def upsert_vector(self, vector_id: str, vector: list[float], metadata: dict[str, Any]) -> bool:
        self._vectors[vector_id] = (vector, metadata)
        return True

    async def query_vector(self, query_vector: list[float], top_k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        results = []
        for vid, (vec, meta) in self._vectors.items():
            results.append((vid, 0.95, meta))
        return results[:top_k]

    async def check_health(self) -> IntegrationHealthReport:
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="InMemoryVector",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=self.status,
            latency_ms=0.5,
        )


class PineconeVectorAdapter(InMemoryVectorAdapter):
    """Extension placeholder for Pinecone Vector DB Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "vector.pinecone"
        self._name = "Pinecone Vector DB Adapter"
        self._priority = 100


class QdrantVectorAdapter(InMemoryVectorAdapter):
    """Extension placeholder for Qdrant Vector DB Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "vector.qdrant"
        self._name = "Qdrant Vector DB Adapter"
        self._priority = 90


class FAISSVectorAdapter(InMemoryVectorAdapter):
    """Extension placeholder for FAISS Vector DB Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "vector.faiss"
        self._name = "FAISS Vector DB Adapter"
        self._priority = 80
