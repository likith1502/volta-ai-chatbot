import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.models.enums import MemoryType

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class Memory(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    """Contextual memory domain entity."""

    __tablename__ = "memories"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    memory_key: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    memory_value: Mapped[str] = mapped_column(Text, nullable=False)
    memory_type: Mapped[MemoryType] = mapped_column(
        Enum(MemoryType, native_enum=False, length=32),
        default=MemoryType.EPISODIC,
        nullable=False,
    )
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="memories",
        passive_deletes=True,
    )
