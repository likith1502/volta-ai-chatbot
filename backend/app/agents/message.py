import uuid
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Inter-agent message communication types."""

    DIRECT = "direct"
    BROADCAST = "broadcast"
    REQUEST = "request"
    RESPONSE = "response"
    DELEGATION = "delegation"


class AgentMessage(BaseModel):
    """Message payload transmitted between agents in an AgentMailbox."""

    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    sender_agent_id: str
    recipient_agent_id: str
    message_type: MessageType = MessageType.DIRECT
    content: str = Field(..., min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: 1786088000.0)
