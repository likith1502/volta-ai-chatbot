import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.search.search_adapter import SearchAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.search.elasticsearch")

try:
    from elasticsearch import AsyncElasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    AsyncElasticsearch = None
    ELASTICSEARCH_AVAILABLE = False


class ElasticsearchSearchAdapter(SearchAdapter):
    """Production Elasticsearch Search Adapter using AsyncElasticsearch SDK with lazy loading and timeouts."""

    def __init__(
        self,
        hosts: str = "http://localhost:9200",
        default_index: str = "volta_search_index",
        request_timeout: float = 15.0,
    ) -> None:
        super().__init__(provider_id="search.elasticsearch", name="Elasticsearch Enterprise Search Adapter", priority=90)
        self.hosts = hosts
        self.default_index = default_index
        self.request_timeout = request_timeout
        self._client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without making external network calls."""
        if context:
            self._context = context

        url = self._context.resolved_secrets.get("ELASTICSEARCH_HOSTS", self.hosts)
        idx = self._context.resolved_secrets.get("ELASTICSEARCH_INDEX", self.default_index)
        self.hosts = url
        self.default_index = idx

        if not ELASTICSEARCH_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("ElasticsearchSearchAdapter initialized without elasticsearch dependency.")
            return

        if not url:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("ElasticsearchSearchAdapter initialized without ELASTICSEARCH_HOSTS.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_client(self) -> Any:
        """Lazily instantiates AsyncElasticsearch client."""
        if not ELASTICSEARCH_AVAILABLE:
            raise RuntimeError("elasticsearch package is unavailable. Install 'elasticsearch' to enable Elasticsearch search adapter.")

        if self._client is None:
            url = self._context.resolved_secrets.get("ELASTICSEARCH_HOSTS", self.hosts)
            api_key = self._context.resolved_secrets.get("ELASTICSEARCH_API_KEY")

            kwargs: dict[str, Any] = {"hosts": [url], "request_timeout": self.request_timeout}
            if api_key:
                kwargs["api_key"] = api_key

            self._client = AsyncElasticsearch(**kwargs)

        return self._client

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not ELASTICSEARCH_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        url = self._context.resolved_secrets.get("ELASTICSEARCH_HOSTS", self.hosts)
        if not url:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically closes AsyncElasticsearch client."""
        if self._client is not None:
            await self._client.close()
            self._client = None

        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Executes full-text match query against Elasticsearch index."""
        client = await self._get_client()
        res = await client.search(
            index=self.default_index,
            query={"match": {"_all": query}} if hasattr(client, "search") else {"match_all": {}},
            size=limit,
        )
        hits = res.get("hits", {}).get("hits", [])
        return [dict(h.get("_source", {})) for h in hits]

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check calling cluster health."""
        start_time = time.perf_counter()

        if not ELASTICSEARCH_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Elasticsearch",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "elasticsearch package not installed"},
            )

        url = self._context.resolved_secrets.get("ELASTICSEARCH_HOSTS", self.hosts)
        if not url:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Elasticsearch",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "ELASTICSEARCH_HOSTS missing from secrets"},
            )

        try:
            client = await self._get_client()
            health = await client.cluster.health()
            latency = (time.perf_counter() - start_time) * 1000.0
            status_color = health.get("status", "red")
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Elasticsearch",
                is_healthy=status_color in ["green", "yellow"],
                health_level=HealthLevel.GREEN if status_color == "green" else HealthLevel.ORANGE,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"cluster_status": status_color, "index": self.default_index},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Elasticsearch",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
