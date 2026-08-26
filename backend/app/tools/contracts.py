import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.tools.manifest import ToolManifest
from app.tools.result import ToolResult


class ToolExecutePayload(BaseModel):
    """Payload for executing a tool call."""

    tool_name: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    conversation_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None


class ToolValidatePayload(BaseModel):
    """Payload for validating tool arguments against JSON schema."""

    tool_name: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolResponse(BaseModel):
    """Response container for single tool operations."""

    manifest: Optional[ToolManifest] = None
    result: Optional[ToolResult] = None
    message: str = "Tool operation completed"
