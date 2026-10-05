from app.agents.definition import AgentDefinition
from app.agents.identity import AgentIdentity
from app.agents.role import AgentRole


def create_research_discovery_team_spec() -> dict:
    """Returns definition specification for Research & Discovery Team."""
    return {
        "team_name": "Research & Discovery Team",
        "supervisor": AgentDefinition(
            identity=AgentIdentity(name="Lead Research Supervisor"),
            role=AgentRole.SUPERVISOR,
        ),
        "workers": [
            AgentDefinition(
                identity=AgentIdentity(name="Data Gathering Worker"),
                role=AgentRole.RESEARCH,
            ),
            AgentDefinition(
                identity=AgentIdentity(name="Synthesis & Review Worker"),
                role=AgentRole.REVIEWER,
            ),
        ],
    }
