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

logger = logging.getLogger("app.integrations.adapters.messaging.rabbitmq")

try:
    import aio_pika
    RABBITMQ_AVAILABLE = True
except ImportError:
    aio_pika = None
    RABBITMQ_AVAILABLE = False


class RabbitMQMessagingAdapter(MessagingAdapter):
    """Production RabbitMQ AMQP Message Queue Adapter using aio-pika SDK with lazy loading and timeouts."""

    def __init__(
        self,
        amqp_url: str = "amqp://guest:guest@localhost:5672/",
        connect_timeout: float = 5.0,
        request_timeout: float = 10.0,
    ) -> None:
        super().__init__(provider_id="messaging.rabbitmq", name="RabbitMQ AMQP Queue Adapter", priority=85)
        self.amqp_url = amqp_url
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._connection: Any = None
        self._channel: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without making external network calls."""
        if context:
            self._context = context

        url = self._context.resolved_secrets.get("RABBITMQ_URL", self.amqp_url)
        self.amqp_url = url

        if not RABBITMQ_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("RabbitMQMessagingAdapter initialized without aio-pika dependency.")
            return

        if not url:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("RabbitMQMessagingAdapter initialized without RABBITMQ_URL.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_channel(self) -> Any:
        """Lazily connects to RabbitMQ and creates channel."""
        if not RABBITMQ_AVAILABLE:
            raise RuntimeError("aio-pika package is unavailable. Install 'aio-pika' to enable RabbitMQ messaging.")

        if self._channel is None or self._connection is None or self._connection.is_closed:
            url = self._context.resolved_secrets.get("RABBITMQ_URL", self.amqp_url)
            self._connection = await aio_pika.connect_robust(url, timeout=self.connect_timeout)
            self._channel = await self._connection.channel()

        return self._channel

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not RABBITMQ_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        url = self._context.resolved_secrets.get("RABBITMQ_URL", self.amqp_url)
        if not url:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically closes RabbitMQ connection and channel."""
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()

        self._connection = None
        self._channel = None
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def publish_message(self, topic_or_url: str, payload: dict[str, Any]) -> bool:
        """Publishes JSON message payload to RabbitMQ routing key / queue."""
        channel = await self._get_channel()
        message = aio_pika.Message(body=json.dumps(payload).encode("utf-8"))
        await channel.default_exchange.publish(message, routing_key=topic_or_url)
        return True

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not RABBITMQ_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="RabbitMQ",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "aio-pika package not installed"},
            )

        url = self._context.resolved_secrets.get("RABBITMQ_URL", self.amqp_url)
        if not url:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="RabbitMQ",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "RABBITMQ_URL missing from secrets"},
            )

        try:
            channel = await self._get_channel()
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="RabbitMQ",
                is_healthy=True,
                health_level=HealthLevel.GREEN,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"amqp_url": self.amqp_url},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="RabbitMQ",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
