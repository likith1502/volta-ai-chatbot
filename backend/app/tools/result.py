import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Immutable tool execution output container."""

    result_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: Optional[uuid.UUID] = None
    tool_id: Optional[uuid.UUID] = None
    tool_name: str = Field(..., min_length=1)
    status: str = Field(default="success", description="'success', 'failed', 'error', 'timed_out', 'skipped'")
    success: bool = True
    output: Any = None
    execution_time_ms: float = Field(default=0.0, ge=0.0)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
