import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from app.hitl.approval_status import ApprovalDecision, ApprovalStatus


class ApprovalSnapshot(BaseModel):
    """Lightweight state snapshot of an approval request for auditing and replay inspection."""

    snapshot_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    approval_id: uuid.UUID
    status: ApprovalStatus
    decision: ApprovalDecision
    history: list[dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
