import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_label(label: str) -> str:
    """Normalizes and canonicalizes a location label.

    Trims whitespace and maps known aliases to canonical title-case ('Home', 'Work').
    Preserves other arbitrary user labels cleanly.
    """
    cleaned = label.strip()
    if not cleaned:
        raise ValueError("Location label cannot be empty or whitespace-only.")
    lower = cleaned.lower()
    if lower == "home":
        return "Home"
    if lower == "work":
        return "Work"
    return cleaned


class SavedLocationCreate(BaseModel):
    """Payload schema for creating a saved location."""

    label: str = Field(
        ..., min_length=1, max_length=100, description="Location label, e.g. Home, Work"
    )
    address: str = Field(
        ..., min_length=1, max_length=500, description="Full street address"
    )
    latitude: Optional[float] = Field(
        None, ge=-90.0, le=90.0, description="Latitude coordinate (-90 to 90)"
    )
    longitude: Optional[float] = Field(
        None, ge=-180.0, le=180.0, description="Longitude coordinate (-180 to 180)"
    )

    @field_validator("address")
    @classmethod
    def validate_address_not_whitespace(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Address cannot be empty or whitespace-only.")
        return v.strip()

    @field_validator("label")
    @classmethod
    def validate_label_not_whitespace(cls, v: str) -> str:
        return normalize_label(v)


class SavedLocationUpdate(BaseModel):
    """Payload schema for updating an existing saved location."""

    label: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Updated location label"
    )
    address: Optional[str] = Field(
        None, min_length=1, max_length=500, description="Updated street address"
    )
    latitude: Optional[float] = Field(
        None, ge=-90.0, le=90.0, description="Updated latitude coordinate"
    )
    longitude: Optional[float] = Field(
        None, ge=-180.0, le=180.0, description="Updated longitude coordinate"
    )

    @field_validator("address")
    @classmethod
    def validate_address_not_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Address cannot be empty or whitespace-only.")
            return v.strip()
        return None

    @field_validator("label")
    @classmethod
    def validate_label_not_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return normalize_label(v)
        return None


class SavedLocationResponse(BaseModel):
    """Response DTO for SavedLocation domain entity."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    label: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
