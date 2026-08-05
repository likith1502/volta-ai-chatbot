from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.events.event_types import EventPriority


class WorkflowEventMetadata(BaseModel):
    """Metadata describing a workflow event origin and specifications."""

    version: str = "1.0.0"
    schema_version: str = "1.0"
    source: str = "workflow_engine"
    producer: str = "system"
    priority: EventPriority = EventPriority.NORMAL
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
