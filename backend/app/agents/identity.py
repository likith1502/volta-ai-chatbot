import uuid
from pydantic import BaseModel, Field


class AgentIdentity(BaseModel):
    """Identity attributes for an agent."""

    agent_id: str = Field(default_factory=lambda: f"agent_{uuid.uuid4().hex[:8]}")
    name: str = Field(..., min_length=1)
    version: str = Field(default="1.0.0")
    description: str = Field(default="Autonomous Enterprise Worker Agent")
    owner: str = Field(default="system")
