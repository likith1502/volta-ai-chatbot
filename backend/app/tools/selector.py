from typing import Optional

from app.tools.manifest import ToolManifest


class ToolSelector:
    """Selects best tool manifests based on name or tag match."""

    def select(
        self, manifests: list[ToolManifest], name: str
    ) -> Optional[ToolManifest]:
        name_lower = name.strip().lower()
        for m in manifests:
            if m.tool_name.lower() == name_lower:
                return m
        return None
