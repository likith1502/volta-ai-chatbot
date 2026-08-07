from pydantic import BaseModel, Field
from app.agents.capabilities import AgentCapabilities
from app.agents.identity import AgentIdentity
from app.agents.persona import AgentPersona
from app.agents.policy import AgentPolicy
from app.agents.role import AgentRole


class AgentManifest(BaseModel):
    """Manifest describing complete specifications of an agent."""

    identity: AgentIdentity
    role: AgentRole = AgentRole.SUPPORT
    persona: AgentPersona = Field(default_factory=AgentPersona)
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    policy: AgentPolicy = Field(default_factory=AgentPolicy)
