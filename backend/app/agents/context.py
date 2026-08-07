import uuid
from typing import Any
from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """Runtime context passed during agent execution turns."""

    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    session_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    inputs: dict[str, Any] = Field(default_factory=dict)
    memory_snapshot: list[dict[str, Any]] = Field(default_factory=list)
    variables: dict[str, Any] = Field(default_factory=dict)
