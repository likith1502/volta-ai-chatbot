import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.events.event_filter import WorkflowEventFilter
from app.events.event_listener import WorkflowEventListener
from app.events.event_types import EventPriority


class EventSubscription(BaseModel):
    """Encapsulates event subscription binding metadata, filters, priority, and listener reference."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    subscription_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    listener: WorkflowEventListener
    filter: Optional[WorkflowEventFilter] = None
    priority: EventPriority = EventPriority.NORMAL
    enabled: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
