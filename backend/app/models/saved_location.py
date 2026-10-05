import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Index, String, UUID, column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class SavedLocation(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    """User saved location domain entity (e.g. Home, Work, etc.)."""

    __tablename__ = "saved_locations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="saved_locations",
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "ix_saved_locations_user_label_active",
            "user_id",
            func.lower(column("label")),
            unique=True,
            postgresql_where=column("is_deleted") == False,  # noqa: E712
            sqlite_where=column("is_deleted") == False,  # noqa: E712
        ),
    )
