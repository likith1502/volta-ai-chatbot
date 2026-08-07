import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field


class NodeExecutionContext(BaseModel):
    """Context snapshot captured for a single node execution turn."""

    node_id: str
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    memory_snapshot: Optional[dict[str, Any]] = None
    tool_snapshot: Optional[dict[str, Any]] = None
    runtime_snapshot: Optional[dict[str, Any]] = None
    prompt_snapshot: Optional[dict[str, Any]] = None
