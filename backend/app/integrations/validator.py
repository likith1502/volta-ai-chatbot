from app.integrations.exceptions import IntegrationException
from app.integrations.manifest import PluginManifest


class IntegrationValidator:
    """Validates adapter manifests and configurations."""

    @staticmethod
    def validate_manifest(manifest: PluginManifest) -> bool:
        if not manifest.id.strip():
            raise IntegrationException("Plugin Manifest ID cannot be empty.")
        if not manifest.name.strip():
            raise IntegrationException("Plugin Manifest Name cannot be empty.")
        return True
