import uuid
from decimal import Decimal
from typing import Any, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.fleet.base import BaseFleetPricingProvider
from app.fleet.demo import DemoFleetPricingProvider
from app.models.recommendation import Recommendation
from app.schemas.cab import CabAvailabilityQuote, LocationPoint
from app.services.base import BaseService
from app.services.recommendation import RecommendationService


class CabPricingService(BaseService):
    """Domain service managing cab availability requests, pricing quotes, and recommendation persistence."""

    def __init__(
        self,
        session: AsyncSession,
        provider: Optional[BaseFleetPricingProvider] = None,
        recommendation_service: Optional[RecommendationService] = None,
    ) -> None:
        super().__init__(session)
        self.provider = provider or DemoFleetPricingProvider()
        self.recommendation_service = recommendation_service or RecommendationService(
            session
        )

    def _normalize_location_point(
        self, location: Union[LocationPoint, str, dict[str, Any]]
    ) -> LocationPoint:
        """Normalizes heterogeneous input formats into a validated domain LocationPoint."""
        if isinstance(location, LocationPoint):
            return location
        if isinstance(location, str):
            cleaned = location.strip()
            if not cleaned:
                raise ValueError("Location string cannot be empty or whitespace-only.")
            return LocationPoint(address=cleaned, label=cleaned)
        if isinstance(location, dict):
            return LocationPoint.model_validate(location)
        raise ValueError(f"Unsupported location representation: {type(location)}")

    async def get_availability_quote(
        self,
        pickup: Union[LocationPoint, str, dict[str, Any]],
        destination: Union[LocationPoint, str, dict[str, Any]],
        conversation_id: Optional[uuid.UUID] = None,
        persist_recommendation: bool = False,
    ) -> CabAvailabilityQuote:
        """Queries the configured fleet provider and returns a validated availability quote.

        Optionally attaches and persists the structured quote into an active conversation's
        Recommendation record via RecommendationService without creating or confirming any booking.
        """
        pickup_point = self._normalize_location_point(pickup)
        dest_point = self._normalize_location_point(destination)

        quote = await self.provider.get_availability_quote(
            pickup=pickup_point,
            destination=dest_point,
        )

        # Validate Quote Integrity
        if not quote.options:
            raise ValueError("Fleet provider returned zero vehicle options.")

        tiers_seen: set[str] = set()
        for opt in quote.options:
            if opt.fare <= Decimal("0.00"):
                raise ValueError(
                    f"Vehicle option '{opt.display_name}' has non-positive fare: {opt.fare}"
                )
            if opt.currency != quote.currency:
                raise ValueError(
                    f"Option currency '{opt.currency}' does not match quote currency '{quote.currency}'."
                )
            if opt.tier.value in tiers_seen:
                raise ValueError(
                    f"Duplicate vehicle tier detected in quote: '{opt.tier.value}'."
                )
            tiers_seen.add(opt.tier.value)

        if quote.expires_at is not None and quote.expires_at <= quote.created_at:
            raise ValueError(
                f"expires_at ({quote.expires_at}) must be strictly after created_at ({quote.created_at})."
            )

        # Optionally persist structured quote inside Recommendation record
        if persist_recommendation and conversation_id:
            rec_data: dict[str, Any] = {
                "quote_id": str(quote.quote_id),
                "pickup": quote.pickup.model_dump(mode="json"),
                "destination": quote.destination.model_dump(mode="json"),
                "currency": quote.currency,
                "options": [
                    {
                        "tier": opt.tier.value,
                        "display_name": opt.display_name,
                        "fare": str(opt.fare),
                        "currency": opt.currency,
                        "eta_minutes": opt.eta_minutes,
                        "capacity": opt.capacity,
                        "description": opt.description,
                    }
                    for opt in quote.options
                ],
                "created_at": quote.created_at.isoformat(),
                "expires_at": quote.expires_at.isoformat()
                if quote.expires_at
                else None,
            }
            rec = await self.recommendation_service.create_recommendation(
                conversation_id=conversation_id,
                recommendation_type="cab_availability",
                recommendation_data=rec_data,
                confidence_score=1.0,
                ranking=1,
            )
            quote.recommendation_id = rec.id

        return quote

    async def get_persisted_recommendation(
        self, recommendation_id: uuid.UUID
    ) -> Recommendation:
        """Retrieves a previously stored recommendation entity by primary key."""
        return await self.recommendation_service.get_recommendation(recommendation_id)
