from app.integrations.exceptions import IntegrationError
from app.integrations.manifest import PluginManifest


class IntegrationValidator:
    """Validates adapter manifests and configurations."""

    @staticmethod
    def validate_manifest(manifest: PluginManifest) -> bool:
        if not manifest.id.strip():
            raise IntegrationError("Plugin Manifest ID cannot be empty.")
        if not manifest.name.strip():
            raise IntegrationError("Plugin Manifest Name cannot be empty.")
        return True
