from typing import Optional

from app.agents.team import AgentTeam


class TeamRegistry:
    """In-memory registry storing configured multi-agent teams."""

    def __init__(self) -> None:
        self._teams: dict[str, AgentTeam] = {}

    def register_team(self, team: AgentTeam) -> None:
        self._teams[team.team_id] = team

    def get_team(self, team_id: str) -> Optional[AgentTeam]:
        return self._teams.get(team_id)

    def list_teams(self) -> list[AgentTeam]:
        return list(self._teams.values())
