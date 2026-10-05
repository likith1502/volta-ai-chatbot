import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.vector.vector_adapter import VectorDatabaseAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.vector.pinecone")

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    pinecone = None
    PINECONE_AVAILABLE = False


class PineconeVectorAdapter(VectorDatabaseAdapter):
    """Production Pinecone Vector DB Adapter using pinecone-client SDK with lazy loading and timeouts."""

    def __init__(
        self,
        index_name: str = "volta-pinecone-index",
        dimension: int = 1536,
        connect_timeout: float = 5.0,
        request_timeout: float = 15.0,
    ) -> None:
        super().__init__(provider_id="vector.pinecone", name="Pinecone Vector DB Adapter", priority=100)
        self.index_name = index_name
        self.dimension = dimension
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._pinecone_client: Any = None
        self._index: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without making network calls."""
        if context:
            self._context = context

        api_key = self._context.resolved_secrets.get("PINECONE_API_KEY")
        index = self._context.resolved_secrets.get("PINECONE_INDEX", self.index_name)
        self.index_name = index

        if not PINECONE_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("PineconeVectorAdapter initialized without pinecone dependency.")
            return

        if not api_key:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("PineconeVectorAdapter initialized without PINECONE_API_KEY.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_index(self) -> Any:
        """Lazily instantiates Pinecone Client and Index."""
        if not PINECONE_AVAILABLE:
            raise RuntimeError("pinecone package is unavailable. Install 'pinecone' to enable Pinecone storage.")

        if self._index is None:
            api_key = self._context.resolved_secrets.get("PINECONE_API_KEY")
            if not api_key:
                raise ValueError("PINECONE_API_KEY missing from context secrets.")

            def _init():
                pc = pinecone.Pinecone(api_key=api_key)
                return pc.Index(self.index_name)

            self._index = await asyncio.to_thread(_init)

        return self._index

    async def connect(self) -> bool:
        """Verifies readiness without network calls."""
        if not PINECONE_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        api_key = self._context.resolved_secrets.get("PINECONE_API_KEY")
        if not api_key:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically resets Pinecone index session."""
        self._index = None
        self._pinecone_client = None
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def upsert_vector(self, vector_id: str, vector: list[float], metadata: dict[str, Any]) -> bool:
        """Upserts a single vector into Pinecone index."""
        index = await self._get_index()

        def _upsert():
            index.upsert(vectors=[(vector_id, vector, metadata)])
            return True

        return await asyncio.to_thread(_upsert)

    async def query_vector(self, query_vector: list[float], top_k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        """Queries nearest neighbors from Pinecone index."""
        index = await self._get_index()

        def _query():
            res = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
            results = []
            for match in res.get("matches", []):
                results.append((str(match["id"]), float(match["score"]), dict(match.get("metadata", {}))))
            return results

        return await asyncio.to_thread(_query)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not PINECONE_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Pinecone",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "pinecone package not installed"},
            )

        api_key = self._context.resolved_secrets.get("PINECONE_API_KEY")
        if not api_key:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Pinecone",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "PINECONE_API_KEY missing from secrets"},
            )

        try:
            index = await self._get_index()

            def _check():
                index.describe_index_stats()

            await asyncio.to_thread(_check)
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Pinecone",
                is_healthy=True,
                health_level=HealthLevel.GREEN,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"index": self.index_name},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Pinecone",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
