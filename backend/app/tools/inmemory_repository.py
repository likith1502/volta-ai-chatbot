from typing import Optional
from app.tools.manifest import ToolManifest
from app.tools.repository import ToolRepository
from app.tools.tool import BaseTool


class InMemoryToolRepository(ToolRepository):
    """In-memory thread-safe reference implementation of ToolRepository."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        self._manifests: dict[str, ToolManifest] = {}

    async def register(self, tool_instance: BaseTool) -> ToolManifest:
        name = tool_instance.name.lower().strip()
        manifest = ToolManifest(
            tool_name=tool_instance.name,
            version=tool_instance.version,
            schema_spec=tool_instance.schema_spec,
        )
        self._tools[name] = tool_instance
        self._manifests[name] = manifest
        return manifest

    async def unregister(self, name: str) -> bool:
        n = name.lower().strip()
        if n in self._tools:
            self._tools.pop(n, None)
            self._manifests.pop(n, None)
            return True
        return False

    async def get_by_name(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name.lower().strip())

    async def get_manifest(self, name: str) -> Optional[ToolManifest]:
        return self._manifests.get(name.lower().strip())

    async def list_all(self) -> list[ToolManifest]:
        return list(self._manifests.values())

    async def clear(self) -> None:
        self._tools.clear()
        self._manifests.clear()
