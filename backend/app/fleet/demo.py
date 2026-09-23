import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.fleet.base import BaseFleetPricingProvider
from app.models.enums import VehicleTier
from app.schemas.cab import CabAvailabilityQuote, CabOption, LocationPoint


class DemoFleetPricingProvider(BaseFleetPricingProvider):
    """Demo fleet pricing provider returning staging telemetry and baseline pricing.

    IMPORTANT ARCHITECTURAL NOTICE:
    The fares defined in this class (Mini ₹180, Sedan ₹240, SUV ₹360) are demonstration
    fixtures constructed solely for local evaluation and staging verification.
    They do NOT represent production fares, distance-matrix calculations, or live
    metered rates. This provider is designed to be seamlessly swapped with a live
    VOLTA dispatch telematics and pricing API via BaseFleetPricingProvider.
    """

    DEMO_CURRENCY = "INR"
    DEMO_QUOTE_EXPIRY_MINUTES = 15

    async def get_available_options(
        self,
        pickup: LocationPoint,
        destination: LocationPoint,
    ) -> list[CabOption]:
        """Returns standard demonstration vehicle options with realistic ETAs and seat capacities."""
        return [
            CabOption(
                tier=VehicleTier.MINI,
                display_name="Mini",
                fare=Decimal("180.00"),
                currency=self.DEMO_CURRENCY,
                eta_minutes=4,
                capacity=4,
                description="Compact city electric hatchback for quick, budget-friendly commutes.",
            ),
            CabOption(
                tier=VehicleTier.SEDAN,
                display_name="Sedan",
                fare=Decimal("240.00"),
                currency=self.DEMO_CURRENCY,
                eta_minutes=6,
                capacity=4,
                description="Premium electric sedan with extra legroom and quiet, comfortable ride.",
            ),
            CabOption(
                tier=VehicleTier.SUV,
                display_name="SUV",
                fare=Decimal("360.00"),
                currency=self.DEMO_CURRENCY,
                eta_minutes=8,
                capacity=6,
                description="Spacious electric SUV suited for groups, luggage, and maximum comfort.",
            ),
        ]

    async def get_availability_quote(
        self,
        pickup: LocationPoint,
        destination: LocationPoint,
    ) -> CabAvailabilityQuote:
        """Constructs a time-bounded availability quote preserving the supplied location points."""
        options = await self.get_available_options(
            pickup=pickup, destination=destination
        )
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=self.DEMO_QUOTE_EXPIRY_MINUTES)

        return CabAvailabilityQuote(
            quote_id=uuid.uuid4(),
            pickup=pickup,
            destination=destination,
            options=options,
            currency=self.DEMO_CURRENCY,
            created_at=now,
            expires_at=expires_at,
        )
