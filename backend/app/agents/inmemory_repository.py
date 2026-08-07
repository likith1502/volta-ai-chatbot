from typing import Optional
from app.agents.agent import Agent
from app.agents.definition import AgentDefinition
from app.agents.repository import AgentRepository


class InMemoryAgentRepository(AgentRepository):
    """In-memory implementation of AgentRepository."""

    def __init__(self) -> None:
        self._definitions: dict[str, AgentDefinition] = {}
        self._agents: dict[str, Agent] = {}

    def save_definition(self, definition: AgentDefinition) -> None:
        self._definitions[definition.definition_id] = definition

    def get_definition(self, definition_id: str) -> Optional[AgentDefinition]:
        return self._definitions.get(definition_id)

    def save_agent(self, agent: Agent) -> None:
        self._agents[agent.agent_id] = agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self._agents.get(agent_id)

    def list_agents(self) -> list[Agent]:
        return list(self._agents.values())
