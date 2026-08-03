import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    """Payload schema for user account registration."""

    full_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    preferred_language: str = "en"


class UserUpdate(BaseModel):
    """Payload schema for updating user profile attributes."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    preferred_language: Optional[str] = None


class UserResponse(BaseModel):
    """Response DTO for User domain entity."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: str
    email: str
    phone_number: Optional[str] = None
    preferred_language: str
    profile_image_url: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
