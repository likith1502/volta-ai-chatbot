"""Enterprise Deployment core models."""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class DeploymentStatus(str, Enum):
    """Operational status of a deployment record."""
    UNKNOWN = "unknown"
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    ROLLEDBACK = "rolledback"
    TERMINATED = "terminated"


class Deployment(BaseModel):
    """Canonical deployment record."""

    model_config = {"arbitrary_types_allowed": True}

    deployment_id: str
    platform_version: str = "7.8.0"
    environment: str = "production"
    strategy: str = "rolling"
    status: DeploymentStatus = DeploymentStatus.UNKNOWN
    replica_count: int = Field(default=1, ge=1)
    image_tag: str = "latest"
    config_hash: str = ""
    created_at: float = Field(default=1786088000.0)
    deployed_at: Optional[float] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)
