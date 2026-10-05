import asyncio
import json
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.messaging.messaging_adapter import MessagingAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.messaging.kafka")

try:
    from aiokafka import AIOKafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    AIOKafkaProducer = None
    KAFKA_AVAILABLE = False


class KafkaMessagingAdapter(MessagingAdapter):
    """Production Apache Kafka Event Bus Adapter using aiokafka SDK with lazy loading and timeouts."""

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        connect_timeout: float = 5.0,
        request_timeout: float = 10.0,
    ) -> None:
        super().__init__(provider_id="messaging.kafka", name="Apache Kafka Event Bus Adapter", priority=90)
        self.bootstrap_servers = bootstrap_servers
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._producer: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without making external network calls."""
        if context:
            self._context = context

        servers = self._context.resolved_secrets.get("KAFKA_BOOTSTRAP_SERVERS", self.bootstrap_servers)
        self.bootstrap_servers = servers

        if not KAFKA_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("KafkaMessagingAdapter initialized without aiokafka dependency.")
            return

        if not servers:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("KafkaMessagingAdapter initialized without bootstrap servers.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_producer(self) -> Any:
        """Lazily creates AIOKafkaProducer instance."""
        if not KAFKA_AVAILABLE:
            raise RuntimeError("aiokafka package is unavailable. Install 'aiokafka' to enable Kafka messaging.")

        if self._producer is None:
            servers = self._context.resolved_secrets.get("KAFKA_BOOTSTRAP_SERVERS", self.bootstrap_servers)
            producer = AIOKafkaProducer(
                bootstrap_servers=servers,
                request_timeout_ms=int(self.request_timeout * 1000),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await producer.start()
            self._producer = producer

        return self._producer

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not KAFKA_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        servers = self._context.resolved_secrets.get("KAFKA_BOOTSTRAP_SERVERS", self.bootstrap_servers)
        if not servers:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically stops Kafka producer."""
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def publish_message(self, topic_or_url: str, payload: dict[str, Any]) -> bool:
        """Publishes JSON event payload to Kafka topic."""
        producer = await self._get_producer()
        await producer.send_and_wait(topic_or_url, payload)
        return True

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not KAFKA_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Kafka",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "aiokafka package not installed"},
            )

        servers = self._context.resolved_secrets.get("KAFKA_BOOTSTRAP_SERVERS", self.bootstrap_servers)
        if not servers:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Kafka",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "KAFKA_BOOTSTRAP_SERVERS missing from secrets"},
            )

        try:
            producer = await self._get_producer()
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Kafka",
                is_healthy=True,
                health_level=HealthLevel.GREEN,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"bootstrap_servers": servers},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Kafka",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
