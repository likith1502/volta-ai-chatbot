from app.agents.definition import AgentDefinition
from app.agents.identity import AgentIdentity
from app.agents.persona import AgentPersona
from app.agents.role import AgentRole


def create_mobility_support_team_spec() -> dict:
    """Returns definition specification for Mobility Support Team."""
    return {
        "team_name": "Volta Mobility Support Team",
        "supervisor": AgentDefinition(
            identity=AgentIdentity(name="Mobility Supervisor Agent"),
            role=AgentRole.SUPERVISOR,
            persona=AgentPersona(
                tone="authoritative", communication_style="structured"
            ),
        ),
        "workers": [
            AgentDefinition(
                identity=AgentIdentity(name="Ride Discovery Agent"),
                role=AgentRole.RESEARCH,
                persona=AgentPersona(communication_style="analytical"),
            ),
            AgentDefinition(
                identity=AgentIdentity(name="Booking Tool Agent"),
                role=AgentRole.TOOL,
                persona=AgentPersona(communication_style="direct"),
            ),
        ],
    }
