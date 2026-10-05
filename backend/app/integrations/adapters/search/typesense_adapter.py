import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.search.search_adapter import SearchAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.search.typesense")

try:
    import typesense
    TYPESENSE_AVAILABLE = True
except ImportError:
    typesense = None
    TYPESENSE_AVAILABLE = False


class TypesenseSearchAdapter(SearchAdapter):
    """Production Typesense Search Adapter using typesense-python SDK with lazy loading and timeouts."""

    def __init__(
        self,
        collection_name: str = "volta_typesense_collection",
        connection_timeout: float = 5.0,
    ) -> None:
        super().__init__(provider_id="search.typesense", name="Typesense Fast Search Adapter", priority=85)
        self.collection_name = collection_name
        self.connection_timeout = connection_timeout
        self._client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without making external network calls."""
        if context:
            self._context = context

        api_key = self._context.resolved_secrets.get("TYPESENSE_API_KEY")
        collection = self._context.resolved_secrets.get("TYPESENSE_COLLECTION", self.collection_name)
        self.collection_name = collection

        if not TYPESENSE_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("TypesenseSearchAdapter initialized without typesense dependency.")
            return

        if not api_key:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("TypesenseSearchAdapter initialized without TYPESENSE_API_KEY.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_client(self) -> Any:
        """Lazily instantiates Typesense Client."""
        if not TYPESENSE_AVAILABLE:
            raise RuntimeError("typesense package is unavailable. Install 'typesense' to enable Typesense search adapter.")

        if self._client is None:
            api_key = self._context.resolved_secrets.get("TYPESENSE_API_KEY")
            host = self._context.resolved_secrets.get("TYPESENSE_HOST", "localhost")
            port = self._context.resolved_secrets.get("TYPESENSE_PORT", "8108")
            protocol = self._context.resolved_secrets.get("TYPESENSE_PROTOCOL", "http")

            if not api_key:
                raise ValueError("TYPESENSE_API_KEY missing from context secrets.")

            def _init():
                return typesense.Client({
                    "nodes": [{"host": host, "port": port, "protocol": protocol}],
                    "api_key": api_key,
                    "connection_timeout_seconds": self.connection_timeout,
                })

            self._client = await asyncio.to_thread(_init)

        return self._client

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not TYPESENSE_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        api_key = self._context.resolved_secrets.get("TYPESENSE_API_KEY")
        if not api_key:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically resets Typesense client session."""
        self._client = None
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Executes search query against Typesense collection."""
        client = await self._get_client()

        def _search():
            res = client.collections[self.collection_name].documents.search({
                "q": query,
                "query_by": "content,title",
                "per_page": limit,
            })
            hits = res.get("hits", [])
            return [dict(h.get("document", {})) for h in hits]

        return await asyncio.to_thread(_search)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check calling health endpoint."""
        start_time = time.perf_counter()

        if not TYPESENSE_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Typesense",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "typesense package not installed"},
            )

        api_key = self._context.resolved_secrets.get("TYPESENSE_API_KEY")
        if not api_key:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Typesense",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "TYPESENSE_API_KEY missing from secrets"},
            )

        try:
            client = await self._get_client()

            def _check():
                return client.operations.is_healthy()

            is_healthy = await asyncio.to_thread(_check)
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Typesense",
                is_healthy=bool(is_healthy),
                health_level=HealthLevel.GREEN if is_healthy else HealthLevel.RED,
                status=IntegrationStatus.CONNECTED if is_healthy else IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"collection": self.collection_name},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Typesense",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
