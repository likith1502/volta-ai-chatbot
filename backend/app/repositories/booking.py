from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.enums import BookingStatus
from app.repositories.base import BaseRepository


class BookingRepository(BaseRepository[Booking]):
    """Domain repository for Booking entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Booking, session)

    async def get_by_reference(self, booking_reference: str, include_deleted: bool = False) -> Booking | None:
        """Retrieves a booking by unique reference code."""
        stmt = select(Booking).where(Booking.booking_reference == booking_reference)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_status(
        self,
        status: BookingStatus,
        offset: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[Booking]:
        """Retrieves bookings filtered by booking status."""
        stmt = select(Booking).where(Booking.booking_status == status)
        stmt = self._apply_soft_delete_filter(stmt, include_deleted)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
