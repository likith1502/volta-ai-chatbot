import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.vector.vector_adapter import VectorDatabaseAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.vector.chroma")

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    chromadb = None
    CHROMA_AVAILABLE = False


class ChromaVectorAdapter(VectorDatabaseAdapter):
    """Production Chroma Vector DB Adapter using chromadb SDK with lazy loading."""

    def __init__(
        self,
        collection_name: str = "volta_chroma_collection",
        connect_timeout: float = 5.0,
        request_timeout: float = 15.0,
    ) -> None:
        super().__init__(provider_id="vector.chroma", name="Chroma Vector DB Adapter", priority=75)
        self.collection_name = collection_name
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._client: Any = None
        self._collection: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without network calls."""
        if context:
            self._context = context

        collection = self._context.resolved_secrets.get("CHROMA_COLLECTION", self.collection_name)
        self.collection_name = collection

        if not CHROMA_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("ChromaVectorAdapter initialized without chromadb dependency.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_collection(self) -> Any:
        """Lazily instantiates Chroma Client and Collection."""
        if not CHROMA_AVAILABLE:
            raise RuntimeError("chromadb package is unavailable. Install 'chromadb' to enable Chroma storage.")

        if self._collection is None:
            host = self._context.resolved_secrets.get("CHROMA_HOST")
            port = int(self._context.resolved_secrets.get("CHROMA_PORT", 8000))

            def _init():
                if host:
                    client = chromadb.HttpClient(host=host, port=port)
                else:
                    client = chromadb.Client()
                return client.get_or_create_collection(self.collection_name)

            self._collection = await asyncio.to_thread(_init)

        return self._collection

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not CHROMA_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically resets Chroma collection session."""
        self._collection = None
        self._client = None
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def upsert_vector(self, vector_id: str, vector: list[float], metadata: dict[str, Any]) -> bool:
        """Upserts vector into Chroma collection."""
        collection = await self._get_collection()

        def _upsert():
            collection.add(
                ids=[vector_id],
                embeddings=[vector],
                metadatas=[metadata],
            )
            return True

        return await asyncio.to_thread(_upsert)

    async def query_vector(self, query_vector: list[float], top_k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        """Queries nearest neighbors from Chroma collection."""
        collection = await self._get_collection()

        def _query():
            res = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
            )
            results = []
            ids = res.get("ids", [[]])[0]
            distances = res.get("distances", [[]])[0] if res.get("distances") else [0.0] * len(ids)
            metadatas = res.get("metadatas", [[]])[0] if res.get("metadatas") else [{}] * len(ids)

            for vid, dist, meta in zip(ids, distances, metadatas):
                score = float(1.0 / (1.0 + float(dist)))
                results.append((str(vid), score, dict(meta or {})))
            return results

        return await asyncio-to-thread(_query) if hasattr(asyncio, "to_thread") else await asyncio.to_thread(_query)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not CHROMA_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Chroma",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "chromadb package not installed"},
            )

        try:
            collection = await self._get_collection()

            def _check():
                return collection.count()

            count = await asyncio.to_thread(_check)
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Chroma",
                is_healthy=True,
                health_level=HealthLevel.GREEN,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"collection": self.collection_name, "count": count},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Chroma",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
