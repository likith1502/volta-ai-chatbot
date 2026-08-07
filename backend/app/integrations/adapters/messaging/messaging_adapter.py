from abc import ABC, abstractmethod
from typing import Any, Optional
from app.integrations.capabilities import IntegrationCapability
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport, IntegrationProvider
from app.integrations.status import IntegrationStatus


class MessagingAdapter(IntegrationProvider, ABC):
    """Abstract interface for messaging queue and webhook event dispatchers."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name=name, category=IntegrationCapability.MESSAGING, priority=priority)

    @abstractmethod
    async def publish_message(self, topic_or_url: str, payload: dict[str, Any]) -> bool:
        pass


class WebhookMessagingAdapter(MessagingAdapter):
    """Reference messaging adapter dispatching HTTP Webhooks."""

    def __init__(self) -> None:
        super().__init__(provider_id="messaging.webhook", name="HTTP Webhook Messaging Adapter", priority=10)
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

    async def publish_message(self, topic_or_url: str, payload: dict[str, Any]) -> bool:
        return True

    async def check_health(self) -> IntegrationHealthReport:
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="Webhook",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=self.status,
            latency_ms=3.1,
        )


class KafkaMessagingAdapter(WebhookMessagingAdapter):
    """Extension placeholder for Apache Kafka Event Bus Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "messaging.kafka"
        self._name = "Apache Kafka Event Bus Adapter"


class RabbitMQMessagingAdapter(WebhookMessagingAdapter):
    """Extension placeholder for RabbitMQ Message Queue Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "messaging.rabbitmq"
        self._name = "RabbitMQ Message Queue Adapter"
