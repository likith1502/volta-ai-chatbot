import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.intent import Intent


class Entity(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    """NLU Slot entity extraction domain entity."""

    __tablename__ = "entities"

    intent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    entity_value: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Relationships
    intent: Mapped["Intent"] = relationship(
        "Intent",
        back_populates="entities",
        passive_deletes=True,
    )
