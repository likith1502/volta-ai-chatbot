import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, Float, ForeignKey, Integer, JSON, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.models.enums import RecommendationStatus

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.conversation import Conversation


class Recommendation(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    """Ride recommendation domain entity."""

    __tablename__ = "recommendations"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    recommendation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    recommendation_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[RecommendationStatus] = mapped_column(
        Enum(RecommendationStatus, native_enum=False, length=32),
        default=RecommendationStatus.PENDING,
        nullable=False,
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="recommendations",
        passive_deletes=True,
    )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="recommendation",
        passive_deletes=True,
        lazy="selectin",
    )
