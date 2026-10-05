from abc import ABC, abstractmethod
from typing import Optional
from app.agents.agent import Agent
from app.agents.definition import AgentDefinition


class AgentRepository(ABC):
    """Abstract Repository interface for storing agent definitions and instances."""

    @abstractmethod
    def save_definition(self, definition: AgentDefinition) -> None:
        pass

    @abstractmethod
    def get_definition(self, definition_id: str) -> Optional[AgentDefinition]:
        pass

    @abstractmethod
    def save_agent(self, agent: Agent) -> None:
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        pass

    @abstractmethod
    def list_agents(self) -> list[Agent]:
        pass
