import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import NotificationType


class NotificationCreate(BaseModel):
    """Payload schema for dispatching a user notification."""

    user_id: uuid.UUID
    notification_type: NotificationType
    title: str
    body: str


class NotificationResponse(BaseModel):
    """Response DTO for Notification domain entity."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    notification_type: NotificationType
    title: str
    body: str
    is_read: bool
    delivery_status: str
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
