import logging
from typing import Optional
from app.agents.agent import Agent
from app.agents.definition import AgentDefinition
from app.agents.repository import AgentRepository
from app.agents.inmemory_repository import InMemoryAgentRepository
from app.agents.role import AgentRole
from app.agents.status import AgentStatus

logger = logging.getLogger("app.agents.registry")


class AgentRegistry:
    """Registry maintaining active agent definitions, worker instances, and dynamic capability discovery."""

    def __init__(self, repository: Optional[AgentRepository] = None) -> None:
        self.repository = repository or InMemoryAgentRepository()

    def register_definition(self, definition: AgentDefinition) -> None:
        self.repository.save_definition(definition)
        logger.info(f"AgentDefinition '{definition.definition_id}' registered for '{definition.identity.name}'")

    def register_agent(self, agent: Agent) -> None:
        self.repository.save_agent(agent)
        logger.info(f"Agent '{agent.agent_id}' ('{agent.name}') registered in AgentRegistry.")

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self.repository.get_agent(agent_id)

    def list_agents(self) -> list[Agent]:
        return self.repository.list_agents()

    def find_by_role(self, role: AgentRole) -> list[Agent]:
        return [a for a in self.list_agents() if a.role == role]

    def find_by_capability(self, capability_name: str) -> list[Agent]:
        results = []
        for a in self.list_agents():
            caps = a.definition.capabilities
            if getattr(caps, f"supports_{capability_name}", False) or capability_name in caps.supported_tools:
                results.append(a)
        return results

    def find_available(self) -> list[Agent]:
        return [a for a in self.list_agents() if a.status in [AgentStatus.IDLE, AgentStatus.WAITING]]

    def find_idle(self) -> list[Agent]:
        return [a for a in self.list_agents() if a.status == AgentStatus.IDLE]
