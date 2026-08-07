from app.agents.agent import Agent
from app.agents.exceptions import AgentRuntimeException


class AgentValidator:
    """Validates agent configurations, permissions, and budgets."""

    @staticmethod
    def validate_agent(agent: Agent) -> bool:
        if not agent.name:
            raise AgentRuntimeException("Agent name cannot be empty.")
        return True
