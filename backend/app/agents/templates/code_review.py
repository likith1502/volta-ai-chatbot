from app.agents.definition import AgentDefinition
from app.agents.identity import AgentIdentity
from app.agents.role import AgentRole


def create_code_review_team_spec() -> dict:
    """Returns definition specification for Code Review Team."""
    return {
        "team_name": "Code Review & QA Team",
        "supervisor": AgentDefinition(
            identity=AgentIdentity(name="Lead QA Supervisor"),
            role=AgentRole.SUPERVISOR,
        ),
        "workers": [
            AgentDefinition(
                identity=AgentIdentity(name="Static Analysis Worker"),
                role=AgentRole.CRITIC,
            ),
            AgentDefinition(
                identity=AgentIdentity(name="Security Auditor Worker"),
                role=AgentRole.REVIEWER,
            ),
        ],
    }
