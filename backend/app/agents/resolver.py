from typing import Optional

from app.agents.agent import Agent


class AgentResolver:
    """Resolves agent references by ID or name."""

    @staticmethod
    def resolve(agent_id: str, agents: list[Agent]) -> Optional[Agent]:
        for a in agents:
            if a.agent_id == agent_id or a.name.lower() == agent_id.lower():
                return a
        return None
