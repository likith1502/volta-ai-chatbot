from typing import Optional

from app.agents.agent import Agent
from app.agents.role import AgentRole


class AgentSelector:
    """Selects target agents from list based on role, persona, or capabilities."""

    @staticmethod
    def select_by_role(agents: list[Agent], role: AgentRole) -> Optional[Agent]:
        matches = [a for a in agents if a.role == role]
        return matches[0] if matches else None
