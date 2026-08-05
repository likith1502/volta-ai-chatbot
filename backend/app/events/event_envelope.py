import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.events.event import WorkflowEvent


class EventEnvelope(BaseModel):
    """
    Wrapper envelope separating transport and delivery metadata from immutable event domain objects.
    Enables future pluggability for WebSockets, Kafka, Redis, or HTTP transport layers.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    envelope_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event: WorkflowEvent
    headers: dict[str, str] = Field(default_factory=dict)
    delivery_metadata: dict[str, Any] = Field(default_factory=dict)
    serialization_format: str = "json"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
