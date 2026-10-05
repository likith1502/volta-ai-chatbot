import uuid
import logging
from typing import Optional
from app.agents.agent import Agent
from app.agents.definition import AgentDefinition
from app.agents.identity import AgentIdentity
from app.agents.instance import AgentInstance
from app.agents.persona import AgentPersona
from app.agents.role import AgentRole
from app.agents.templates.mobility_support import create_mobility_support_team_spec
from app.agents.templates.travel_booking import create_travel_booking_team_spec

logger = logging.getLogger("app.agents.factory")


class AgentFactory:
    """Factory creating specialized AgentDefinitions, worker instances, template teams, and agent clones."""

    @staticmethod
    def create_worker(name: str, role: AgentRole = AgentRole.SUPPORT, persona: Optional[AgentPersona] = None) -> Agent:
        identity = AgentIdentity(name=name)
        definition = AgentDefinition(identity=identity, role=role, persona=persona or AgentPersona())
        instance = AgentInstance(definition_id=definition.definition_id)
        return Agent(definition=definition, instance=instance)

    @staticmethod
    def create_from_template(template_name: str) -> dict:
        if template_name == "mobility_support":
            return create_mobility_support_team_spec()
        elif template_name == "travel_booking":
            return create_travel_booking_team_spec()
        else:
            return create_mobility_support_team_spec()

    @staticmethod
    def clone_agent(source_agent: Agent, new_name: Optional[str] = None) -> Agent:
        new_identity = AgentIdentity(name=new_name or f"{source_agent.name} Clone")
        new_def = AgentDefinition(
            identity=new_identity,
            role=source_agent.role,
            persona=source_agent.definition.persona.model_copy(),
            capabilities=source_agent.definition.capabilities.model_copy(),
            policy=source_agent.definition.policy.model_copy(),
            profile=source_agent.definition.profile.model_copy(),
        )
        return Agent(definition=new_def)
