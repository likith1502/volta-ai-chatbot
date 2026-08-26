from abc import ABC, abstractmethod
from typing import Optional

from app.tools.manifest import ToolManifest
from app.tools.tool import BaseTool


class ToolRepository(ABC):
    """Abstract Base Class defining storage contracts for Tool manifests and instances."""

    @abstractmethod
    async def register(self, tool_instance: BaseTool) -> ToolManifest:
        """Registers a BaseTool instance and returns its ToolManifest."""
        pass

    @abstractmethod
    async def unregister(self, name: str) -> bool:
        """Unregisters tool by name."""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[BaseTool]:
        """Retrieves BaseTool instance by name."""
        pass

    @abstractmethod
    async def get_manifest(self, name: str) -> Optional[ToolManifest]:
        """Retrieves ToolManifest by tool name."""
        pass

    @abstractmethod
    async def list_all(self) -> list[ToolManifest]:
        """Lists all registered ToolManifest entries."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clears all registered tools."""
        pass
