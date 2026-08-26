import logging

from pydantic import BaseModel, Field

logger = logging.getLogger("app.tools.health")


class ToolHealthStatus(BaseModel):
    """Health status report for Tool Runtime."""

    is_healthy: bool = True
    total_registered_tools: int = Field(default=0, ge=0)
    active_tools_count: int = Field(default=0, ge=0)
    status: str = "Tool Runtime is healthy"


class ToolHealthManager:
    """Centralized health orchestrator checking Tool Repository readiness."""

    def __init__(self, registry) -> None:
        self.registry = registry

    async def check_health(self) -> ToolHealthStatus:
        repo = self.registry.get_repository()
        all_tools = await repo.list_all()
        active = [t for t in all_tools if not t.deprecated]

        return ToolHealthStatus(
            is_healthy=True,
            total_registered_tools=len(all_tools),
            active_tools_count=len(active),
            status=f"Tool Runtime operational with {len(active)} active tools.",
        )
