import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin
from app.models.enums import ConversationSource, ConversationStatus

if TYPE_CHECKING:
    from app.models.intent import Intent
    from app.models.memory import Memory
    from app.models.message import Message
    from app.models.recommendation import Recommendation
    from app.models.user import User


class Conversation(UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    """Dialogue conversation session domain entity."""

    __tablename__ = "conversations"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    session_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    source: Mapped[ConversationSource] = mapped_column(
        Enum(ConversationSource, native_enum=False, length=32),
        default=ConversationSource.WEB,
        nullable=False,
    )
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus, native_enum=False, length=32),
        default=ConversationStatus.ACTIVE,
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="conversations",
        passive_deletes=True,
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    memories: Mapped[list["Memory"]] = relationship(
        "Memory",
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    intents: Mapped[list["Intent"]] = relationship(
        "Intent",
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
