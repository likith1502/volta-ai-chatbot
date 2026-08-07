import logging
from typing import Optional
from app.tools.manifest import ToolManifest
from app.tools.permission import ToolPermission
from app.tools.repository import ToolRepository
from app.tools.type import ToolType

logger = logging.getLogger("app.tools.discovery")


class ToolDiscoveryService:
    """Tool Discovery Service querying registered tool manifests by type, capabilities, permissions, and tags."""

    def __init__(self, repository: ToolRepository) -> None:
        self.repository = repository

    async def find_tools(
        self,
        tool_type: Optional[ToolType] = None,
        permission: Optional[ToolPermission] = None,
        supports_async: Optional[bool] = None,
        supports_batch: Optional[bool] = None,
        tags: Optional[list[str]] = None,
    ) -> list[ToolManifest]:
        """Queries registered tool manifests matching criteria."""
        all_manifests = await self.repository.list_all()
        matched = []

        for m in all_manifests:
            if m.deprecated:
                continue
            if permission and m.required_permission != permission:
                continue
            if supports_async is not None and m.capabilities.supports_async != supports_async:
                continue
            if supports_batch is not None and m.capabilities.supports_batch != supports_batch:
                continue
            matched.append(m)

        return matched
