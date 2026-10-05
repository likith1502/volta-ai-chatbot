import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.vector.vector_adapter import VectorDatabaseAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.vector.faiss")

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    faiss = None
    np = None
    FAISS_AVAILABLE = False


class FAISSVectorAdapter(VectorDatabaseAdapter):
    """Production FAISS Vector DB Adapter using faiss CPU/GPU SDK with lazy loading."""

    def __init__(self, dimension: int = 1536) -> None:
        super().__init__(provider_id="vector.faiss", name="FAISS Vector DB Adapter", priority=80)
        self.dimension = dimension
        self._index: Any = None
        self._id_map: dict[int, str] = {}
        self._metadata_map: dict[str, dict[str, Any]] = {}
        self._next_id = 0
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without network calls."""
        if context:
            self._context = context

        if not FAISS_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("FAISSVectorAdapter initialized without faiss dependency.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_index(self) -> Any:
        """Lazily instantiates FAISS IndexFlatL2."""
        if not FAISS_AVAILABLE:
            raise RuntimeError("faiss package is unavailable. Install 'faiss-cpu' to enable FAISS vector storage.")

        if self._index is None:
            def _init():
                return faiss.IndexFlatL2(self.dimension)

            self._index = await asyncio.to_thread(_init)

        return self._index

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not FAISS_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically resets FAISS index resources."""
        self._index = None
        self._id_map.clear()
        self._metadata_map.clear()
        self._next_id = 0
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def upsert_vector(self, vector_id: str, vector: list[float], metadata: dict[str, Any]) -> bool:
        """Upserts vector into FAISS index."""
        index = await self._get_index()

        def _upsert():
            vec_np = np.array([vector], dtype=np.float32)
            index.add(vec_np)
            numeric_id = self._next_id
            self._next_id += 1
            self._id_map[numeric_id] = vector_id
            self._metadata_map[vector_id] = metadata
            return True

        return await asyncio.to_thread(_upsert)

    async def query_vector(self, query_vector: list[float], top_k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        """Queries nearest neighbors from FAISS index."""
        index = await self._get_index()

        def _query():
            if index.ntotal == 0:
                return []
            q_np = np.array([query_vector], dtype=np.float32)
            distances, indices = index.search(q_np, min(top_k, index.ntotal))
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx in self._id_map:
                    vid = self._id_map[idx]
                    meta = self._metadata_map.get(vid, {})
                    # Convert L2 distance to score (1 / (1 + dist))
                    score = float(1.0 / (1.0 + float(dist)))
                    results.append((vid, score, meta))
            return results

        return await asyncio.to_thread(_query)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not FAISS_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="FAISS",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "faiss package not installed"},
            )

        try:
            index = await self._get_index()
            total = getattr(index, "ntotal", 0)
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="FAISS",
                is_healthy=True,
                health_level=HealthLevel.GREEN,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"total_vectors": total, "dimension": self.dimension},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="FAISS",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "operation_failure", "message": str(exc)},
            )
