import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enums import BookingStatus


class BookingCreate(BaseModel):
    """Payload schema for booking a ride from a recommendation."""

    recommendation_id: uuid.UUID
    provider: str = "volta_fleet"
    external_booking_id: Optional[str] = None


class BookingResponse(BaseModel):
    """Response DTO for Booking domain entity."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recommendation_id: Optional[uuid.UUID] = None
    booking_reference: str
    booking_status: BookingStatus
    provider: str
    external_booking_id: Optional[str] = None
    booked_at: Optional[datetime] = None
