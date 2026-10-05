from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_cab_pricing_service
from app.schemas.cab import CabAvailabilityQuote, CabAvailabilityRequest
from app.schemas.common import ResponseEnvelope
from app.services.cab_pricing import CabPricingService
from app.utils.responses import success_response

router = APIRouter(prefix="/cabs", tags=["Cabs & Pricing"])


@router.post(
    "/quote",
    response_model=ResponseEnvelope[CabAvailabilityQuote],
    status_code=status.HTTP_200_OK,
    summary="Get Cab Availability Quote",
    description="Queries available vehicle options and pricing quotes for pickup and destination.",
)
async def get_cab_quote(
    payload: CabAvailabilityRequest,
    service: CabPricingService = Depends(get_cab_pricing_service),
) -> ResponseEnvelope[CabAvailabilityQuote]:
    """Generates an availability quote with vehicle tiers and pricing."""
    quote = await service.get_availability_quote(
        pickup=payload.pickup,
        destination=payload.destination,
        conversation_id=payload.conversation_id,
        persist_recommendation=bool(payload.conversation_id),
    )
    return success_response(
        data=quote,
        message="Cab availability quote generated successfully.",
    )
