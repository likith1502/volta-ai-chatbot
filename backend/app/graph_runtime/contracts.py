import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.graph_runtime.execution_result import GraphExecutionResult
from app.graph_runtime.state import GraphRuntimeState


class GraphExecutePayload(BaseModel):
    """Payload to execute a graph workflow runtime request."""

    workflow_id: str = "default_workflow"
    conversation_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GraphResumePayload(BaseModel):
    """Payload to resume a paused/interrupted graph execution session."""

    session_id: uuid.UUID
    approval_granted: bool = True
    input_overrides: dict[str, Any] = Field(default_factory=dict)


class GraphPausePayload(BaseModel):
    """Payload to pause a running graph execution session."""

    session_id: uuid.UUID
    reason: str = "User pause request"


class GraphCancelPayload(BaseModel):
    """Payload to cancel a graph execution session."""

    session_id: uuid.UUID
    reason: str = "User cancel request"


class GraphResponse(BaseModel):
    """API response container for graph operations."""

    message: str = "Operation completed"
    result: Optional[GraphExecutionResult] = None
