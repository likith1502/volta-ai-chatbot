"""Deployment configuration models."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeploymentConfig:
    """Global deployment configuration."""

    platform_version: str = "7.8.0"
    default_environment: str = "production"
    default_strategy: str = "rolling"
    default_image_tag: str = "latest"
    registry_url: str = "ghcr.io/likith1502/volta-ai-chatbot"
    health_check_interval_seconds: int = 30
    deployment_timeout_seconds: int = 300
    rollback_on_validation_failure: bool = True
    enable_auto_scaling: bool = True
    enable_backup: bool = True
    enable_dr: bool = True
    enable_observability: bool = True
    extra: dict[str, Any] = field(default_factory=dict)
