from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ChannelType(str, Enum):
    """Supported external enterprise messaging channels."""

    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"


class InboundMessage(BaseModel):
    """Normalized inbound message from an external messaging platform."""

    channel: ChannelType
    external_message_id: str
    external_user_id: str
    sender_name: str | None = None
    content: str
    timestamp: datetime | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OutboundMessage(BaseModel):
    """Canonical outbound message to dispatch to an external messaging channel."""

    channel: ChannelType
    recipient_id: str
    content: str
    reply_to_message_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DeliveryReceipt(BaseModel):
    """Delivery or read status event from a messaging channel."""

    channel: ChannelType
    message_id: str
    status: str
    timestamp: datetime | None = None
    recipient_id: str | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class WebhookVerificationResult(BaseModel):
    """Result of incoming webhook verification and signature authentication."""

    is_valid: bool
    challenge_response: str | None = None
    error_message: str | None = None
    status_code: int = 200
