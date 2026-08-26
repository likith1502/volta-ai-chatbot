import logging
from typing import Optional

from app.agents.definition import AgentDefinition
from app.agents.instance import AgentInstance
from app.agents.lifecycle import AgentLifecycleState
from app.agents.permissions import AgentPermission
from app.agents.role import AgentRole
from app.agents.status import AgentStatus

logger = logging.getLogger("app.agents.agent")


class Agent:
    """Core domain class encapsulating AgentDefinition blueprint and active AgentInstance worker state."""

    def __init__(
        self, definition: AgentDefinition, instance: Optional[AgentInstance] = None
    ) -> None:
        self.definition = definition
        self.instance = instance or AgentInstance(
            definition_id=definition.definition_id
        )

    @property
    def agent_id(self) -> str:
        return self.definition.identity.agent_id

    @property
    def name(self) -> str:
        return self.definition.identity.name

    @property
    def role(self) -> AgentRole:
        return self.definition.role

    @property
    def status(self) -> AgentStatus:
        return self.instance.status

    def set_status(self, status: AgentStatus) -> None:
        self.instance.status = status

    def transition_lifecycle(self, state: AgentLifecycleState) -> bool:
        return self.instance.lifecycle.transition_to(state)

    def has_permission(self, permission: AgentPermission) -> bool:
        return self.definition.policy.permissions.has_permission(permission)

    def is_budget_exhausted(self) -> bool:
        return self.definition.policy.budget.is_exhausted()
