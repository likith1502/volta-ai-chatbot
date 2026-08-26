from app.agents.definition import AgentDefinition
from app.agents.identity import AgentIdentity
from app.agents.role import AgentRole


def create_travel_booking_team_spec() -> dict:
    """Returns definition specification for Travel Booking Team."""
    return {
        "team_name": "Travel Booking Team",
        "supervisor": AgentDefinition(
            identity=AgentIdentity(name="Travel Supervisor Agent"),
            role=AgentRole.SUPERVISOR,
        ),
        "workers": [
            AgentDefinition(
                identity=AgentIdentity(name="Itinerary Planner Agent"),
                role=AgentRole.PLANNER,
            ),
            AgentDefinition(
                identity=AgentIdentity(name="Hotel & Flight Research Agent"),
                role=AgentRole.RESEARCH,
            ),
        ],
    }
