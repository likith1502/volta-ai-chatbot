import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import ConversationSource, ConversationStatus


class ConversationCreate(BaseModel):
    """Payload schema for initializing a conversation session."""

    user_id: uuid.UUID
    session_id: str
    source: ConversationSource = ConversationSource.WEB
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    """Response DTO for Conversation domain entity."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    session_id: str
    source: ConversationSource
    title: Optional[str] = None
    status: ConversationStatus
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
