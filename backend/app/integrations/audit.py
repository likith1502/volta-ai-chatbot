import logging
import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("app.integrations.audit")


class IntegrationAuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"aud_{uuid.uuid4().hex[:8]}")
    provider_id: str
    action: str  # Register, Configure, HealthCheck, SecretAccess, Reconnect, Failure, Recovery
    details: dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: 1786088000.0)


class IntegrationAuditLogger:
    """Audit logging engine for provider events."""

    def __init__(self) -> None:
        self._events: list[IntegrationAuditEvent] = []

    def log_event(
        self, provider_id: str, action: str, details: Optional[dict[str, Any]] = None
    ) -> IntegrationAuditEvent:
        evt = IntegrationAuditEvent(
            provider_id=provider_id, action=action, details=details or {}
        )
        self._events.append(evt)
        logger.info(f"IntegrationAuditLogger: [{action}] provider '{provider_id}'")
        return evt

    def get_events(
        self, provider_id: Optional[str] = None
    ) -> list[IntegrationAuditEvent]:
        if provider_id:
            return [e for e in self._events if e.provider_id == provider_id]
        return list(self._events)
