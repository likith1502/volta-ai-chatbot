from typing import Any

from pydantic import BaseModel, Field

from app.integrations.capabilities import CapabilityFeatureFlags, IntegrationCapability


class PluginManifest(BaseModel):
    """Specification manifest defining adapter identity, version compatibility, and capabilities."""

    id: str = Field(..., min_length=1)  # e.g., "storage.filesystem"
    name: str = Field(..., min_length=1)
    version: str = "1.0.0"
    api_version: str = "v1"
    runtime_version: str = "7.7.0"
    category: IntegrationCapability = IntegrationCapability.STORAGE
    author: str = "VOLTA Core Team"
    license: str = "MIT"
    depends_on: list[str] = Field(default_factory=list)
    optional_dependencies: list[str] = Field(default_factory=list)
    conflicts_with: list[str] = Field(default_factory=list)
    capabilities: CapabilityFeatureFlags = Field(default_factory=CapabilityFeatureFlags)
    configuration_schema: dict[str, Any] = Field(default_factory=dict)
