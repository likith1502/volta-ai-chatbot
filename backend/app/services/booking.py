import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.domain import BookingNotFoundException, InvalidBookingStatusException, RecommendationExpiredException, RecommendationNotFoundException
from app.models.booking import Booking
from app.models.enums import BookingStatus, NotificationType, RecommendationStatus
from app.models.notification import Notification
from app.repositories.base import BaseRepository
from app.repositories.booking import BookingRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.recommendation import RecommendationRepository
from app.services.base import BaseService


class BookingService(BaseService):
    """Application domain service for Ride Bookings and complex transactional workflow orchestration."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.booking_repo = BookingRepository(session)
        self.recommendation_repo = RecommendationRepository(session)
        self.conversation_repo = ConversationRepository(session)
        self.notification_repo = BaseRepository(Notification, session)

    async def create_booking_from_recommendation(
        self,
        recommendation_id: uuid.UUID,
        provider: str = "volta_fleet",
        external_booking_id: Optional[str] = None,
    ) -> Booking:
        """Orchestrates creating a ride booking from an active AI recommendation payload."""
        recommendation = await self.recommendation_repo.get_by_id(recommendation_id)
        if not recommendation:
            raise RecommendationNotFoundException(f"Recommendation with ID '{recommendation_id}' not found.")

        if recommendation.status == RecommendationStatus.EXPIRED:
            raise RecommendationExpiredException("Cannot create booking from an expired recommendation.")

        if recommendation.status != RecommendationStatus.PENDING:
            raise InvalidBookingStatusException(f"Recommendation status is '{recommendation.status}', must be PENDING.")

        ref_code = f"BK-{uuid.uuid4().hex[:8].upper()}"

        booking = await self.booking_repo.create(
            {
                "recommendation_id": recommendation_id,
                "booking_reference": ref_code,
                "booking_status": BookingStatus.CONFIRMED,
                "provider": provider,
                "external_booking_id": external_booking_id,
            }
        )

        await self.recommendation_repo.update(
            recommendation_id,
            {"status": RecommendationStatus.ACCEPTED},
        )

        conversation = await self.conversation_repo.get_by_id(recommendation.conversation_id)
        if conversation and conversation.user_id:
            await self.notification_repo.create(
                {
                    "user_id": conversation.user_id,
                    "notification_type": NotificationType.BOOKING_UPDATE,
                    "title": "Ride Booking Confirmed",
                    "body": f"Your ride booking {ref_code} has been successfully confirmed.",
                    "is_read": False,
                    "delivery_status": "sent",
                }
            )

        await self.commit()
        return booking

    async def get_booking_by_reference(self, booking_reference: str) -> Booking:
        """Retrieves a booking reservation by unique reference code."""
        booking = await self.booking_repo.get_by_reference(booking_reference)
        if not booking:
            raise BookingNotFoundException(f"Booking with reference '{booking_reference}' not found.")
        return booking

    async def cancel_booking(self, booking_id: uuid.UUID) -> Booking:
        """Cancels an active booking reservation."""
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundException(f"Booking with ID '{booking_id}' not found.")

        if booking.booking_status == BookingStatus.CANCELLED:
            raise InvalidBookingStatusException("Booking is already cancelled.")

        cancelled = await self.booking_repo.update(
            booking_id,
            {"booking_status": BookingStatus.CANCELLED},
        )
        if not cancelled:
            raise BookingNotFoundException(f"Booking with ID '{booking_id}' not found.")

        await self.commit()
        return cancelled
