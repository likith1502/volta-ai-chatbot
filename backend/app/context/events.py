import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class WorkflowEventType(str, Enum):
    """Event types generated throughout workflow orchestration lifecycle."""

    USER_MESSAGE = "user_message"
    AI_RESPONSE = "ai_response"
    TOOL_STARTED = "tool_started"
    TOOL_COMPLETED = "tool_completed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    INTERRUPTED = "interrupted"
    RESUMED = "resumed"


class WorkflowEvent(BaseModel):
    """Lightweight event telemetry object representing workflow state transitions."""

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: WorkflowEventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    conversation_id: uuid.UUID
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
