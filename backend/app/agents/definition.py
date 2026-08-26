import uuid

from pydantic import BaseModel, Field

from app.agents.capabilities import AgentCapabilities
from app.agents.identity import AgentIdentity
from app.agents.manifest import AgentManifest
from app.agents.persona import AgentPersona
from app.agents.policy import AgentPolicy
from app.agents.profile import AgentProfile
from app.agents.role import AgentRole


class AgentDefinition(BaseModel):
    """Blueprint model defining an agent template/deployment spec."""

    definition_id: str = Field(default_factory=lambda: f"def_{uuid.uuid4().hex[:8]}")
    identity: AgentIdentity
    role: AgentRole = AgentRole.SUPPORT
    persona: AgentPersona = Field(default_factory=AgentPersona)
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    policy: AgentPolicy = Field(default_factory=AgentPolicy)
    profile: AgentProfile = Field(default_factory=AgentProfile)

    def to_manifest(self) -> AgentManifest:
        return AgentManifest(
            identity=self.identity,
            role=self.role,
            persona=self.persona,
            capabilities=self.capabilities,
            policy=self.policy,
        )
