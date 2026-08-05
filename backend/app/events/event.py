import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.events.event_metadata import WorkflowEventMetadata
from app.events.event_status import WorkflowEventStatus
from app.events.event_types import WorkflowEventCategory, WorkflowEventType


class WorkflowEvent(BaseModel):
    """
    Immutable domain telemetry event emitted during workflow execution traversal.
    Events represent state change occurrences and are strictly read-only informational objects.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: WorkflowEventType
    category: WorkflowEventCategory = WorkflowEventCategory.SYSTEM
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    workflow_id: Optional[str] = None
    execution_id: Optional[uuid.UUID] = None
    graph_id: Optional[str] = None
    node_id: Optional[str] = None
    correlation_id: Optional[str] = None
    status: WorkflowEventStatus = WorkflowEventStatus.CREATED
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: WorkflowEventMetadata = Field(default_factory=WorkflowEventMetadata)
