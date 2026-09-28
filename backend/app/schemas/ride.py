import uuid
from decimal import Decimal
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.cab import LocationPoint


class RideSlotStatus(str, Enum):
    """Lifecycle states for conversational ride slot extraction, quoting, and booking."""

    NOT_REQUESTED = "not_requested"
    NEEDS_BOTH = "needs_both"
    NEEDS_PICKUP = "needs_pickup"
    NEEDS_DESTINATION = "needs_destination"
    RESOLVED = "resolved"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    BOOKED = "booked"
    CANCELLED = "cancelled"


class RideEntityState(BaseModel):
    """Strongly-typed entity state tracking collected ride slots and booking state across turns."""

    model_config = ConfigDict(from_attributes=True)

    pickup_raw: Optional[str] = None
    destination_raw: Optional[str] = None
    pickup_point: Optional[LocationPoint] = None
    destination_point: Optional[LocationPoint] = None
    status: RideSlotStatus = RideSlotStatus.NOT_REQUESTED
    clarification_question: Optional[str] = None
    is_cancelled: bool = False

    # Quoting and Booking Integration Fields
    recommendation_id: Optional[uuid.UUID] = None
    available_options: list[dict[str, Any]] = Field(default_factory=list)
    selected_tier: Optional[str] = None
    selected_fare: Optional[Decimal] = None
    selected_display_name: Optional[str] = None
    booking_id: Optional[uuid.UUID] = None
    booking_reference: Optional[str] = None
    booking_status: Optional[str] = None
    is_booked: bool = False

    last_updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_complete(self) -> bool:
        """Returns True if both pickup and destination are resolved and ready for quoting."""
        return self.status == RideSlotStatus.RESOLVED

    @property
    def is_awaiting_confirmation(self) -> bool:
        """Returns True if a vehicle tier is selected and awaiting explicit user confirmation."""
        return self.status == RideSlotStatus.AWAITING_CONFIRMATION

    @property
    def needs_clarification(self) -> bool:
        """Returns True if the ride request is active but missing pickup or destination."""
        return self.status in (
            RideSlotStatus.NEEDS_BOTH,
            RideSlotStatus.NEEDS_PICKUP,
            RideSlotStatus.NEEDS_DESTINATION,
        )

