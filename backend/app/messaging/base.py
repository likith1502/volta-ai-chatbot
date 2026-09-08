from abc import ABC, abstractmethod
from typing import Any

from app.messaging.models import (
    ChannelType,
    InboundMessage,
    OutboundMessage,
    WebhookVerificationResult,
)


class BaseMessagingAdapter(ABC):
    """Abstract interface for external messaging platform channel adapters."""

    channel: ChannelType

    @abstractmethod
    def verify_webhook(
        self,
        headers: dict[str, str],
        raw_body: bytes,
        query_params: dict[str, str],
    ) -> WebhookVerificationResult:
        """Verifies webhook authentication, HMAC signature, or challenge."""
        pass

    @abstractmethod
    def parse_inbound(self, payload: dict[str, Any]) -> list[InboundMessage]:
        """Parses a platform-specific webhook payload into normalized InboundMessages."""
        pass

    @abstractmethod
    def format_outbound(
        self,
        content: str,
        recipient_id: str,
        reply_to_message_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> OutboundMessage:
        """Formats canonical AI response text into a channel OutboundMessage."""
        pass

    @abstractmethod
    async def send_outbound(
        self,
        message: OutboundMessage,
        client: Any | None = None,
    ) -> bool:
        """Dispatches outbound message to the external messaging platform API."""
        pass
