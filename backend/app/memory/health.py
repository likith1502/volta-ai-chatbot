import logging
from pydantic import BaseModel, Field
from app.memory.registry import MemoryRegistry

logger = logging.getLogger("app.memory.health")


class MemoryHealthStatus(BaseModel):
    """Health status report for Memory Runtime."""

    is_healthy: bool = True
    repository_size: int = Field(default=0, ge=0)
    cleanup_needed: bool = False
    token_pressure: float = Field(default=0.0, ge=0.0, le=1.0)
    status: str = "Memory Runtime is healthy"


class MemoryHealthManager:
    """Centralized health orchestrator checking Memory Repository readiness and capacity status."""

    def __init__(self, registry: MemoryRegistry) -> None:
        self.registry = registry

    async def check_health(self) -> MemoryHealthStatus:
        repo = self.registry.get_repository()
        all_mems = await repo.list_all(limit=1000)
        repo_size = len(all_mems)

        return MemoryHealthStatus(
            is_healthy=True,
            repository_size=repo_size,
            cleanup_needed=repo_size > 1500,
            token_pressure=min(1.0, repo_size / 2000.0),
            status=f"Memory Runtime operational with {repo_size} stored memory entries.",
        )
