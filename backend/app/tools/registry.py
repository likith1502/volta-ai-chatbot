import logging
from typing import Optional
from app.tools.inmemory_repository import InMemoryToolRepository
from app.tools.manifest import ToolManifest
from app.tools.repository import ToolRepository
from app.tools.tool import BaseTool

logger = logging.getLogger("app.tools.registry")


class ToolRegistry:
    """Registry managing active ToolRepository implementations."""

    def __init__(self, repository: Optional[ToolRepository] = None) -> None:
        self.repository = repository or InMemoryToolRepository()

    def set_repository(self, repository: ToolRepository) -> None:
        self.repository = repository

    def get_repository(self) -> ToolRepository:
        return self.repository

    async def register(self, tool_instance: BaseTool) -> ToolManifest:
        return await self.repository.register(tool_instance)

    async def lookup(self, name: str) -> Optional[BaseTool]:
        return await self.repository.get_by_name(name)
