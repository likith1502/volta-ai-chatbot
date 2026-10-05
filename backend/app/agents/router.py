import logging
from typing import Optional
from app.agents.agent import Agent
from app.agents.role import AgentRole

logger = logging.getLogger("app.agents.router")


class AgentRouter:
    """Routes incoming user requests to the optimal supervisor or worker agent."""

    def __init__(self) -> None:
        pass

    def route_request(self, intent: str, registered_agents: list[Agent]) -> Optional[Agent]:
        """Selects target agent by intent and role."""
        if "book" in intent.lower() or "mobility" in intent.lower():
            for a in registered_agents:
                if a.role == AgentRole.SUPERVISOR or a.role == AgentRole.SUPPORT:
                    return a
        if registered_agents:
            return registered_agents[0]
        return None
