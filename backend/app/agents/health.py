from pydantic import BaseModel, Field
from app.agents.registry import AgentRegistry


class AgentHealthStatus(BaseModel):
    is_healthy: bool = True
    registered_agents_count: int = Field(default=0, ge=0)
    status: str = "Multi-Agent Runtime operational"
    components: dict[str, str] = Field(
        default_factory=lambda: {
            "registry": "healthy",
            "task_queue": "healthy",
            "communication_manager": "healthy",
            "delegation_manager": "healthy",
            "team_manager": "healthy",
        }
    )


class AgentHealthManager:
    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    async def check_health(self) -> AgentHealthStatus:
        count = len(self.registry.list_agents())
        return AgentHealthStatus(
            is_healthy=True,
            registered_agents_count=count,
            status="Multi-Agent Runtime operational",
        )
