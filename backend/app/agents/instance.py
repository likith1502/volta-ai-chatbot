import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.agents.lifecycle import AgentLifecycleManager
from app.agents.state import AgentState
from app.agents.status import AgentStatus


class AgentInstance(BaseModel):
    """Active worker pod instance spawned from an AgentDefinition."""

    instance_id: str = Field(default_factory=lambda: f"inst_{uuid.uuid4().hex[:8]}")
    definition_id: str
    status: AgentStatus = AgentStatus.IDLE
    lifecycle: AgentLifecycleManager = Field(default_factory=AgentLifecycleManager)
    state: AgentState = Field(default_factory=AgentState)
    active_task_id: Optional[str] = None
