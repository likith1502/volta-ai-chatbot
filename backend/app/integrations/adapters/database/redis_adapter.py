import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.database.database_adapter import DatabaseAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.database.redis")

try:
    import redis.asyncio as redis_async
    REDIS_AVAILABLE = True
except ImportError:
    redis_async = None
    REDIS_AVAILABLE = False


class RedisDatabaseAdapter(DatabaseAdapter):
    """Production Redis Key-Value & Cache Database Adapter using redis.asyncio SDK with lazy loading and timeouts."""

    def __init__(
        self,
        url: Optional[str] = None,
        connect_timeout: float = 5.0,
        request_timeout: float = 10.0,
    ) -> None:
        super().__init__(provider_id="database.redis", name="Redis Cache & Key-Value Adapter", priority=15)
        self.url = url
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without making network calls."""
        if context:
            self._context = context

        redis_url = self._context.resolved_secrets.get("REDIS_URL", self.url)
        self.url = redis_url

        if not REDIS_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("RedisDatabaseAdapter initialized without redis dependency.")
            return

        if not redis_url:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("RedisDatabaseAdapter initialized without REDIS_URL.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_client(self) -> Any:
        """Lazily creates redis.asyncio client."""
        if not REDIS_AVAILABLE:
            raise RuntimeError("redis package is unavailable. Install 'redis' to enable Redis database adapter.")

        if self._client is None:
            url = self._context.resolved_secrets.get("REDIS_URL", self.url)
            if not url:
                raise ValueError("REDIS_URL missing from context secrets.")

            self._client = redis_async.from_url(
                url,
                socket_connect_timeout=self.connect_timeout,
                socket_timeout=self.request_timeout,
            )

        return self._client

    async def connect(self) -> bool:
        """Verifies readiness without connecting to Redis."""
        if not REDIS_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        url = self._context.resolved_secrets.get("REDIS_URL", self.url)
        if not url:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically closes Redis client connection pool."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def execute_query(self, query: str) -> Any:
        """Capability Honesty: Relational SQL queries are not supported on Redis key-value store."""
        return {
            "error": "unsupported_operation",
            "message": "Redis is a key-value store and does not support SQL execute_query. Use get/set/delete operations.",
        }

    async def get(self, key: str) -> Optional[str]:
        """Gets value by key from Redis."""
        client = await self._get_client()
        val = await client.get(key)
        if val is not None and isinstance(val, bytes):
            return val.decode("utf-8")
        return val

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Sets key-value pair with optional TTL in seconds."""
        client = await self._get_client()
        if ttl is not None:
            return await client.setex(key, ttl, value)
        return await client.set(key, value)

    async def delete(self, key: str) -> bool:
        """Deletes key from Redis."""
        client = await self._get_client()
        res = await client.delete(key)
        return res > 0

    async def expire(self, key: str, ttl: int) -> bool:
        """Sets expiration TTL on key."""
        client = await self._get_client()
        return await client.expire(key, ttl)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check executing PING."""
        start_time = time.perf_counter()

        if not REDIS_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Redis",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "redis package not installed"},
            )

        url = self._context.resolved_secrets.get("REDIS_URL", self.url)
        if not url:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Redis",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "REDIS_URL missing from secrets"},
            )

        try:
            client = await self._get_client()
            res = await client.ping()
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Redis",
                is_healthy=bool(res),
                health_level=HealthLevel.GREEN,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"ping_response": bool(res)},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Redis",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
