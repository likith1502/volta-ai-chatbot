import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatMessage(BaseModel):
    """Conversational turn message schema."""

    model_config = ConfigDict(from_attributes=True)

    role: str
    content: str
    model_used: Optional[str] = None
    token_count: Optional[int] = None
    created_at: Optional[datetime] = None


class ChatUsage(BaseModel):
    """Conversational AI usage metrics schema."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatRequest(BaseModel):
    """Payload schema for sending a user chat message."""

    user_id: uuid.UUID
    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Response DTO for AI chat interaction."""

    conversation_id: uuid.UUID
    session_id: str
    message: ChatMessage
    recommendation_id: Optional[uuid.UUID] = None
    usage: ChatUsage = Field(default_factory=ChatUsage)
