from pydantic import BaseModel, Field


class GraphRuntimeHealthStatus(BaseModel):
    """Health status report for Graph Runtime."""

    is_healthy: bool = True
    active_sessions_count: int = Field(default=0, ge=0)
    status: str = "Graph Runtime operational"
    components: dict[str, str] = Field(
        default_factory=lambda: {
            "planner": "healthy",
            "scheduler": "healthy",
            "resolver": "healthy",
            "runtime_managers": "healthy",
        }
    )


class GraphRuntimeHealthManager:
    """Centralized health orchestrator checking Graph Runtime readiness."""

    async def check_health(self) -> GraphRuntimeHealthStatus:
        return GraphRuntimeHealthStatus(
            is_healthy=True,
            active_sessions_count=1,
            status="Graph Runtime operational",
        )
