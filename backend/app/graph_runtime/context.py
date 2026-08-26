import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field


class GraphRuntimeContext(BaseModel):
    """Runtime execution context aggregating conversation state across workflow execution."""

    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: str = "default_workflow"
    state_data: dict[str, Any] = Field(default_factory=dict)
    memory_context: Optional[dict[str, Any]] = None
    prompt_context: Optional[dict[str, Any]] = None
    tool_context: Optional[dict[str, Any]] = None
    runtime_context: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
