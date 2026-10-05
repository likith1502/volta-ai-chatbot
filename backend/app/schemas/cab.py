import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import VehicleTier


class LocationPoint(BaseModel):
    """Structured location point representing pickup or destination."""

    model_config = ConfigDict(from_attributes=True)

    address: Optional[str] = None
    label: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    saved_location_id: Optional[uuid.UUID] = None

    @model_validator(mode="after")
    def validate_has_identifier(self) -> "LocationPoint":
        """Ensures at least one descriptive location attribute is present."""
        if (
            not self.address
            and not self.label
            and self.latitude is None
            and self.longitude is None
            and self.saved_location_id is None
        ):
            raise ValueError(
                "LocationPoint must contain at least address, label, coordinates, or saved_location_id."
            )
        return self


class CabOption(BaseModel):
    """Available vehicle tier option with estimated pricing and ETA."""

    model_config = ConfigDict(from_attributes=True)

    tier: VehicleTier
    display_name: str = Field(..., min_length=1, max_length=100)
    fare: Decimal = Field(..., gt=Decimal("0.00"))
    currency: str = Field(..., pattern=r"^[A-Z]{3}$")
    eta_minutes: int = Field(..., ge=0)
    capacity: int = Field(..., ge=1)
    description: Optional[str] = None


class CabAvailabilityRequest(BaseModel):
    """Request schema for querying cab availability and pricing quotes."""

    pickup: LocationPoint
    destination: LocationPoint
    conversation_id: Optional[uuid.UUID] = None
    user_id: Optional[uuid.UUID] = None


class CabAvailabilityQuote(BaseModel):
    """Time-bounded cab availability and pricing quote."""

    model_config = ConfigDict(from_attributes=True)

    quote_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    pickup: LocationPoint
    destination: LocationPoint
    options: list[CabOption] = Field(..., min_length=1)
    currency: str = Field("INR", pattern=r"^[A-Z]{3}$")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    recommendation_id: Optional[uuid.UUID] = None

    @model_validator(mode="after")
    def validate_quote_integrity(self) -> "CabAvailabilityQuote":
        """Validates option currencies, tier uniqueness, and expiration window."""
        if not self.options:
            raise ValueError(
                "Quote must contain at least one available vehicle option."
            )

        # Ensure all options match quote currency
        for opt in self.options:
            if opt.currency != self.currency:
                raise ValueError(
                    f"Option currency '{opt.currency}' does not match quote currency '{self.currency}'."
                )

        # Ensure vehicle tiers are unique
        tiers = [opt.tier for opt in self.options]
        if len(tiers) != len(set(tiers)):
            raise ValueError("Quote contains duplicate vehicle tiers.")

        # Validate expiration window
        if self.expires_at is not None and self.expires_at <= self.created_at:
            raise ValueError(
                f"expires_at ({self.expires_at}) must be after created_at ({self.created_at})."
            )

        return self
