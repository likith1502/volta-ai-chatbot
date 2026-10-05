import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field
from app.agents.status import AgentStatus


class AgentSession(BaseModel):
    """Session state tracking active agent worker turns."""

    session_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    agent_id: str
    status: AgentStatus = AgentStatus.IDLE
    active_task_id: Optional[str] = None
    created_at: float = Field(default_factory=lambda: 1786088000.0)
