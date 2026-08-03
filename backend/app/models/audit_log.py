import uuid
from typing import Any, Optional

from sqlalchemy import JSON, String, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class AuditLog(UUIDMixin, TimestampMixin, Base):
    """Immutable system audit log entity."""

    __tablename__ = "audit_logs"

    event_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        nullable=True,
    )
    resource_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    event_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "event_metadata",
        JSON,
        nullable=True,
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
