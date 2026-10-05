from abc import ABC, abstractmethod
from typing import Any, Optional
from app.integrations.capabilities import IntegrationCapability
from app.integrations.provider import IntegrationProvider


class MessagingAdapter(IntegrationProvider, ABC):
    """Abstract interface for event streaming, message queue, and webhook brokers."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name=name, category=IntegrationCapability.MESSAGING, priority=priority)

    @abstractmethod
    async def publish_message(self, topic_or_url: str, payload: dict[str, Any]) -> bool:
        pass


def __getattr__(name: str) -> Any:
    if name == "WebhookMessagingAdapter":
        from app.integrations.adapters.messaging.webhook_adapter import WebhookMessagingAdapter
        return WebhookMessagingAdapter
    if name == "KafkaMessagingAdapter":
        from app.integrations.adapters.messaging.kafka_adapter import KafkaMessagingAdapter
        return KafkaMessagingAdapter
    if name == "RabbitMQMessagingAdapter":
        from app.integrations.adapters.messaging.rabbitmq_adapter import RabbitMQMessagingAdapter
        return RabbitMQMessagingAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "MessagingAdapter",
    "WebhookMessagingAdapter",
    "KafkaMessagingAdapter",
    "RabbitMQMessagingAdapter",
]
