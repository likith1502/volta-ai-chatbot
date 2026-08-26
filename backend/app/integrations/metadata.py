from typing import Any

from pydantic import BaseModel, Field


class IntegrationMetadata(BaseModel):
    """Adapter metadata payload."""

    provider_id: str
    name: str
    category: str
    adapter_version: str = "1.0.0"
    minimum_platform_version: str = "7.0.0"
    maximum_platform_version: str = "8.0.0"
    author: str = "VOLTA Engineering"
    extra: dict[str, Any] = Field(default_factory=dict)
