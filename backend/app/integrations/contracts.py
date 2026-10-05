from typing import Any, Optional
from pydantic import BaseModel, Field


class IntegrationProviderRegisterPayload(BaseModel):
    provider_id: str = Field(..., min_length=1)  # e.g. "storage.filesystem"
    name: str = Field(..., min_length=1)
    category: str = "storage"
    priority: int = Field(default=10, ge=1)
    options: dict[str, Any] = Field(default_factory=dict)


class IntegrationConfigurePayload(BaseModel):
    provider_id: str
    options: dict[str, Any] = Field(default_factory=dict)


class IntegrationTestPayload(BaseModel):
    provider_id: str
    sample_payload: dict[str, Any] = Field(default_factory=dict)


class IntegrationResponse(BaseModel):
    success: bool = True
    data: dict[str, Any]
    message: str = "Integration operation completed"
