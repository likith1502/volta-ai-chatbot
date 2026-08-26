from app.tools.manifest import ToolManifest
from app.tools.result import ToolResult


class ToolSerializer:
    """Serialization helpers for tool results and manifests."""

    @staticmethod
    def result_to_json(result: ToolResult) -> str:
        return result.model_dump_json(indent=2)

    @staticmethod
    def manifest_to_json(manifest: ToolManifest) -> str:
        return manifest.model_dump_json(indent=2)
