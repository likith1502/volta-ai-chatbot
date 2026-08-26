"""Deployment registry — tracks active deployments by ID."""

from __future__ import annotations

from typing import Optional

from app.deployment.deployment import Deployment, DeploymentStatus


class DeploymentRegistry:
    """Registry of all tracked deployments."""

    def __init__(self) -> None:
        self._deployments: dict[str, Deployment] = {}

    def register(self, deployment: Deployment) -> None:
        self._deployments[deployment.deployment_id] = deployment

    def get(self, deployment_id: str) -> Optional[Deployment]:
        return self._deployments.get(deployment_id)

    def list_all(self) -> list[Deployment]:
        return list(self._deployments.values())

    def list_by_status(self, status: DeploymentStatus) -> list[Deployment]:
        return [d for d in self._deployments.values() if d.status == status]

    def list_by_environment(self, environment: str) -> list[Deployment]:
        return [d for d in self._deployments.values() if d.environment == environment]

    def update_status(self, deployment_id: str, status: DeploymentStatus) -> bool:
        d = self._deployments.get(deployment_id)
        if not d:
            return False
        d.status = status
        return True

    def remove(self, deployment_id: str) -> bool:
        if deployment_id not in self._deployments:
            return False
        del self._deployments[deployment_id]
        return True

    @property
    def total_count(self) -> int:
        return len(self._deployments)
