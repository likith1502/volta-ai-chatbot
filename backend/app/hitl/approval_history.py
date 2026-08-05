import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.hitl.approval_status import ApprovalDecision, HumanRole


class ApprovalHistoryRecord(BaseModel):
    """Immutable audit record logging a reviewer's decision or action on an approval request."""

    record_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    approval_id: uuid.UUID
    reviewer: str
    role: HumanRole = HumanRole.REVIEWER
    decision: ApprovalDecision = ApprovalDecision.NONE
    comments: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ApprovalHistory(BaseModel):
    """Immutable audit history recording reviewer decisions and escalation steps."""

    records: list[ApprovalHistoryRecord] = Field(default_factory=list)

    def record_decision(
        self,
        approval_id: uuid.UUID,
        reviewer: str,
        decision: ApprovalDecision,
        role: HumanRole = HumanRole.REVIEWER,
        comments: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ApprovalHistoryRecord:
        """Records a new decision entry into history."""
        rec = ApprovalHistoryRecord(
            approval_id=approval_id,
            reviewer=reviewer,
            role=role,
            decision=decision,
            comments=comments,
            metadata=metadata or {},
        )
        self.records.append(rec)
        return rec
