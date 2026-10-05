import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.vector.vector_adapter import VectorDatabaseAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.vector.qdrant")

try:
    import qdrant_client
    from qdrant_client.models import Distance, PointStruct, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    qdrant_client = None
    PointStruct = None
    VectorParams = None
    Distance = None
    QDRANT_AVAILABLE = False


class QdrantVectorAdapter(VectorDatabaseAdapter):
    """Production Qdrant Vector Database Adapter using qdrant-client SDK with lazy loading and timeouts."""

    def __init__(
        self,
        collection_name: str = "volta_vectors",
        vector_size: int = 1536,
        connect_timeout: float = 5.0,
        request_timeout: float = 15.0,
    ) -> None:
        super().__init__(provider_id="vector.qdrant", name="Qdrant Vector DB Adapter", priority=90)
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without making external network calls."""
        if context:
            self._context = context

        host = self._context.resolved_secrets.get("QDRANT_HOST")
        api_key = self._context.resolved_secrets.get("QDRANT_API_KEY")
        collection = self._context.resolved_secrets.get("QDRANT_COLLECTION", self.collection_name)
        self.collection_name = collection

        if not QDRANT_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("QdrantVectorAdapter initialized without qdrant-client dependency.")
            return

        if not host and not api_key:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("QdrantVectorAdapter initialized without QDRANT_HOST or QDRANT_API_KEY.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_client(self) -> Any:
        """Lazily instantiates qdrant-client."""
        if not QDRANT_AVAILABLE:
            raise RuntimeError("qdrant-client package is unavailable. Install 'qdrant-client' to enable Qdrant storage.")

        if self._client is None:
            host = self._context.resolved_secrets.get("QDRANT_HOST", "localhost")
            api_key = self._context.resolved_secrets.get("QDRANT_API_KEY")
            port = int(self._context.resolved_secrets.get("QDRANT_PORT", 6333))

            def _init():
                return qdrant_client.QdrantClient(
                    host=host,
                    port=port,
                    api_key=api_key,
                    timeout=self.request_timeout,
                )

            self._client = await asyncio.to_thread(_init)

        return self._client

    async def connect(self) -> bool:
        """Verifies readiness without initiating network calls."""
        if not QDRANT_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        host = self._context.resolved_secrets.get("QDRANT_HOST")
        if not host:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically closes Qdrant client connection."""
        if self._client is not None:
            def _close():
                if hasattr(self._client, "close"):
                    self._client.close()

            await asyncio.to_thread(_close)
            self._client = None

        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def upsert_vector(self, vector_id: str, vector: list[float], metadata: dict[str, Any]) -> bool:
        """Upserts a single vector point into Qdrant collection."""
        client = await self._get_client()

        def _upsert():
            point = PointStruct(id=vector_id, vector=vector, payload=metadata)
            client.upsert(collection_name=self.collection_name, points=[point])
            return True

        return await asyncio.to_thread(_upsert)

    async def query_vector(self, query_vector: list[float], top_k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        """Queries nearest neighbors from Qdrant collection."""
        client = await self._get_client()

        def _query():
            hits = client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
            )
            return [(str(h.id), float(h.score), dict(h.payload or {})) for h in hits]

        return await asyncio.to_thread(_query)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not QDRANT_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Qdrant",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "qdrant-client package not installed"},
            )

        host = self._context.resolved_secrets.get("QDRANT_HOST")
        if not host:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Qdrant",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "QDRANT_HOST missing from secrets"},
            )

        try:
            client = await self._get_client()

            def _check():
                client.get_collections()

            await asyncio.to_thread(_check)
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Qdrant",
                is_healthy=True,
                health_level=HealthLevel.GREEN,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"collection": self.collection_name},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Qdrant",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
