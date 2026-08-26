import logging
from typing import Optional

from app.agents.team import AgentTeam, TeamStatus
from app.agents.team_registry import TeamRegistry

logger = logging.getLogger("app.agents.team_manager")


class TeamManager:
    """Manages team creation, registry, and execution state lifecycle."""

    def __init__(self, registry: Optional[TeamRegistry] = None) -> None:
        self.registry = registry or TeamRegistry()

    def create_team(
        self, name: str, supervisor_id: str, member_ids: list[str]
    ) -> AgentTeam:
        team = AgentTeam(
            name=name,
            supervisor_agent_id=supervisor_id,
            member_agent_ids=member_ids,
            status=TeamStatus.READY,
        )
        self.registry.register_team(team)
        logger.info(f"Team '{name}' created with supervisor '{supervisor_id}'")
        return team

    def get_team(self, team_id: str) -> Optional[AgentTeam]:
        return self.registry.get_team(team_id)

    def set_team_status(self, team_id: str, status: TeamStatus) -> None:
        team = self.get_team(team_id)
        if team:
            team.status = status
