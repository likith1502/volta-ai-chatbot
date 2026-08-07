"""Deployment contracts — Pydantic DTO payloads for REST API layer."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class DeploymentValidatePayload(BaseModel):
    deployment_id: str
    platform_version: str = "7.8.0"
    environment: str = "production"
    config: dict[str, Any] = Field(default_factory=dict)


class DeploymentDeployPayload(BaseModel):
    deployment_id: str
    image_tag: str = "latest"
    strategy: str = "rolling"
    environment: str = "production"
    replica_count: int = Field(default=2, ge=1)
    config: dict[str, Any] = Field(default_factory=dict)


class DeploymentRollbackPayload(BaseModel):
    deployment_id: str
    snapshot_id: str
    strategy: str = "rolling"


class DeploymentScalePayload(BaseModel):
    deployment_id: str
    target_replicas: int = Field(ge=1)
    reason: str = "manual"


class DeploymentStatusResponse(BaseModel):
    deployment_id: str
    status: str
    lifecycle_state: str
    environment: str
    replica_count: int
    ready_replicas: int
    health_level: str
    platform_version: str
