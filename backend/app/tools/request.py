import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field


class ToolRequest(BaseModel):
    """Immutable tool execution request payload."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: Optional[uuid.UUID] = None
    conversation_id: Optional[uuid.UUID] = None
    tool_name: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
