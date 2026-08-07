"""Deployment context — runtime metadata passed to adapters."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeploymentContext:
    deployment_id: str = ""
    environment: str = "production"
    platform_version: str = "7.8.0"
    operator: str = "system"
    dry_run: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
