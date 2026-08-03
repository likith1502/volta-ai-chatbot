import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.entity import Entity


class Intent(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    """NLU Intent classification domain entity."""

    __tablename__ = "intents"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    intent_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="intents",
        passive_deletes=True,
    )
    entities: Mapped[list["Entity"]] = relationship(
        "Entity",
        back_populates="intent",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
