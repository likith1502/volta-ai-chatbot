import logging
from typing import Optional

from app.agents.agent import Agent
from app.agents.definition import AgentDefinition
from app.agents.identity import AgentIdentity
from app.agents.role import AgentRole

logger = logging.getLogger("app.agents.coordinator")


class CoordinatorAgent(Agent):
    """Specialized Agent coordinating multi-agent message routing and workflow steps."""

    def __init__(self, definition: Optional[AgentDefinition] = None) -> None:
        def_obj = definition or AgentDefinition(
            identity=AgentIdentity(name="Coordinator Agent"),
            role=AgentRole.SUPERVISOR,
        )
        super().__init__(definition=def_obj)
