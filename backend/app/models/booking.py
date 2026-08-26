import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import UUID, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.models.enums import BookingStatus

if TYPE_CHECKING:
    from app.models.recommendation import Recommendation


class Booking(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    """Ride booking reservation domain entity."""

    __tablename__ = "bookings"

    recommendation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recommendations.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    booking_reference: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    booking_status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, native_enum=False, length=32),
        default=BookingStatus.PENDING,
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(
        String(100), default="volta_fleet", nullable=False
    )
    external_booking_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        index=True,
        nullable=True,
    )
    booked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    recommendation: Mapped[Optional["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="bookings",
        passive_deletes=True,
    )
