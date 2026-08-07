import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field


class ToolContext(BaseModel):
    """Runtime execution context passed into tool execution handlers."""

    conversation_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None
    memory_context: Optional[dict[str, Any]] = None
    runtime_context: Optional[dict[str, Any]] = None
    prompt_context: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
