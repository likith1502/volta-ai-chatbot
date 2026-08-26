from pydantic import BaseModel, Field

from app.agents.budget import AgentExecutionBudget
from app.agents.permissions import AgentPermissionSet


class AgentPolicy(BaseModel):
    """Aggregate policy binding execution budget and permission sets."""

    budget: AgentExecutionBudget = Field(default_factory=AgentExecutionBudget)
    permissions: AgentPermissionSet = Field(default_factory=AgentPermissionSet)
    require_human_approval: bool = False
    allow_parallel_tasks: bool = True
