import uuid

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_booking_service
from app.schemas.booking import BookingCreate, BookingResponse
from app.schemas.common import ResponseEnvelope
from app.services.booking import BookingService
from app.utils.responses import success_response

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=ResponseEnvelope[BookingResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Ride Booking",
    description="Reserves a ride booking from an active AI recommendation.",
)
async def create_booking(
    payload: BookingCreate,
    service: BookingService = Depends(get_booking_service),
):
    booking = await service.create_booking_from_recommendation(
        recommendation_id=payload.recommendation_id,
        provider=payload.provider,
        external_booking_id=payload.external_booking_id,
    )
    return success_response(
        data=BookingResponse.model_validate(booking),
        message="Ride booking created successfully.",
    )


@router.get(
    "/{booking_reference}",
    response_model=ResponseEnvelope[BookingResponse],
    summary="Get Booking By Reference",
    description="Retrieves a ride booking reservation by unique reference code.",
)
async def get_booking(
    booking_reference: str,
    service: BookingService = Depends(get_booking_service),
):
    booking = await service.get_booking_by_reference(booking_reference)
    return success_response(
        data=BookingResponse.model_validate(booking),
        message="Ride booking retrieved successfully.",
    )


@router.patch(
    "/{booking_id}/cancel",
    response_model=ResponseEnvelope[BookingResponse],
    summary="Cancel Ride Booking",
    description="Cancels an active ride booking reservation.",
)
async def cancel_booking(
    booking_id: uuid.UUID,
    service: BookingService = Depends(get_booking_service),
):
    booking = await service.cancel_booking(booking_id)
    return success_response(
        data=BookingResponse.model_validate(booking),
        message="Ride booking cancelled successfully.",
    )
