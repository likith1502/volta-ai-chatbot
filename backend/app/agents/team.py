import uuid
from enum import Enum

from pydantic import BaseModel, Field


class TeamStatus(str, Enum):
    """Execution status of a multi-agent team."""

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentTeam(BaseModel):
    """Composition model for a multi-agent team."""

    team_id: str = Field(default_factory=lambda: f"team_{uuid.uuid4().hex[:8]}")
    name: str = Field(..., min_length=1)
    description: str = Field(default="Multi-Agent Task Execution Team")
    supervisor_agent_id: str
    member_agent_ids: list[str] = Field(default_factory=list)
    status: TeamStatus = TeamStatus.CREATED
