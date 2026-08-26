"""Cloud platform deployment placeholders — AWS, Azure, GCP, Render, Railway, Fly.io, DigitalOcean.

These are lightweight extension stubs establishing stable adapter IDs.
No cloud SDK is imported. All logic is delegated to the cloud provider's CLI/API via subprocess or HTTP.
"""

from __future__ import annotations

from typing import Any


class AWSAdapter:
    """Placeholder — AWS ECS/EKS deployment adapter."""

    adapter_id = "cloud.aws"
    name = "AWS Cloud Adapter"

    async def deploy(self, deployment_id: str, image_tag: str) -> dict[str, Any]:
        return {
            "adapter": self.adapter_id,
            "deployment_id": deployment_id,
            "provider": "aws",
            "status": "pending_implementation",
        }

    async def health_check(self) -> dict[str, Any]:
        return {
            "adapter": self.adapter_id,
            "healthy": True,
            "note": "placeholder — implement AWS SDK integration",
        }


class AzureAdapter:
    """Placeholder — Azure Container Apps deployment adapter."""

    adapter_id = "cloud.azure"
    name = "Azure Cloud Adapter"

    async def deploy(self, deployment_id: str, image_tag: str) -> dict[str, Any]:
        return {
            "adapter": self.adapter_id,
            "deployment_id": deployment_id,
            "provider": "azure",
            "status": "pending_implementation",
        }

    async def health_check(self) -> dict[str, Any]:
        return {
            "adapter": self.adapter_id,
            "healthy": True,
            "note": "placeholder — implement Azure SDK integration",
        }


class GCPAdapter:
    """Placeholder — Google Cloud Run deployment adapter."""

    adapter_id = "cloud.gcp"
    name = "Google Cloud Adapter"

    async def deploy(self, deployment_id: str, image_tag: str) -> dict[str, Any]:
        return {
            "adapter": self.adapter_id,
            "deployment_id": deployment_id,
            "provider": "gcp",
            "status": "pending_implementation",
        }

    async def health_check(self) -> dict[str, Any]:
        return {
            "adapter": self.adapter_id,
            "healthy": True,
            "note": "placeholder — implement GCP SDK integration",
        }


class RenderAdapter:
    """Placeholder — Render deployment adapter."""

    adapter_id = "cloud.render"
    name = "Render Cloud Adapter"

    async def deploy(self, deployment_id: str, image_tag: str) -> dict[str, Any]:
        return {
            "adapter": self.adapter_id,
            "deployment_id": deployment_id,
            "provider": "render",
            "status": "pending_implementation",
        }

    async def health_check(self) -> dict[str, Any]:
        return {"adapter": self.adapter_id, "healthy": True}


class RailwayAdapter:
    """Placeholder — Railway deployment adapter."""

    adapter_id = "cloud.railway"
    name = "Railway Cloud Adapter"

    async def deploy(self, deployment_id: str, image_tag: str) -> dict[str, Any]:
        return {
            "adapter": self.adapter_id,
            "deployment_id": deployment_id,
            "provider": "railway",
            "status": "pending_implementation",
        }

    async def health_check(self) -> dict[str, Any]:
        return {"adapter": self.adapter_id, "healthy": True}


class FlyIOAdapter:
    """Placeholder — Fly.io deployment adapter."""

    adapter_id = "cloud.flyio"
    name = "Fly.io Cloud Adapter"

    async def deploy(self, deployment_id: str, image_tag: str) -> dict[str, Any]:
        return {
            "adapter": self.adapter_id,
            "deployment_id": deployment_id,
            "provider": "flyio",
            "status": "pending_implementation",
        }

    async def health_check(self) -> dict[str, Any]:
        return {"adapter": self.adapter_id, "healthy": True}


class DigitalOceanAdapter:
    """Placeholder — DigitalOcean App Platform deployment adapter."""

    adapter_id = "cloud.digitalocean"
    name = "DigitalOcean Cloud Adapter"

    async def deploy(self, deployment_id: str, image_tag: str) -> dict[str, Any]:
        return {
            "adapter": self.adapter_id,
            "deployment_id": deployment_id,
            "provider": "digitalocean",
            "status": "pending_implementation",
        }

    async def health_check(self) -> dict[str, Any]:
        return {"adapter": self.adapter_id, "healthy": True}
