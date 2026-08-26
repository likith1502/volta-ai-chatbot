from app.integrations.manifest import PluginManifest
from app.integrations.provider import IntegrationHealthReport


class IntegrationSerializer:
    @staticmethod
    def health_report_to_json(report: IntegrationHealthReport) -> str:
        return report.model_dump_json(indent=2)

    @staticmethod
    def manifest_to_json(manifest: PluginManifest) -> str:
        return manifest.model_dump_json(indent=2)
