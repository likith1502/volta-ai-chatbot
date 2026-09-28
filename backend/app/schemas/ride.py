from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.cab import LocationPoint


class RideSlotStatus(str, Enum):
    """Lifecycle states for conversational ride slot extraction and quote readiness."""

    NOT_REQUESTED = "not_requested"
    NEEDS_BOTH = "needs_both"
    NEEDS_PICKUP = "needs_pickup"
    NEEDS_DESTINATION = "needs_destination"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class RideEntityState(BaseModel):
    """Strongly-typed entity state tracking collected ride slots across conversation turns."""

    model_config = ConfigDict(from_attributes=True)

    pickup_raw: Optional[str] = None
    destination_raw: Optional[str] = None
    pickup_point: Optional[LocationPoint] = None
    destination_point: Optional[LocationPoint] = None
    status: RideSlotStatus = RideSlotStatus.NOT_REQUESTED
    clarification_question: Optional[str] = None
    is_cancelled: bool = False
    last_updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @property
    def is_complete(self) -> bool:
        """Returns True if both pickup and destination are resolved and ready for quoting."""
        return self.status == RideSlotStatus.RESOLVED

    @property
    def needs_clarification(self) -> bool:
        """Returns True if the ride request is active but missing pickup or destination."""
        return self.status in (
            RideSlotStatus.NEEDS_BOTH,
            RideSlotStatus.NEEDS_PICKUP,
            RideSlotStatus.NEEDS_DESTINATION,
        )
