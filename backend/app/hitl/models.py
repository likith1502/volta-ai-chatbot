"""Consolidated Models Module for Hitl Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from app.hitl.approval_status import ApprovalDecision
from app.hitl.approval_status import ApprovalDecision, ApprovalStatus
from app.hitl.approval_status import ApprovalPriority
from app.hitl.approval_status import ApprovalStatus, ApprovalDecision
from app.hitl.approval_status import HumanRole
from app.hitl.exceptions import GovernanceException
from datetime import datetime, timezone
from pydantic import BaseModel
from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, Field
from typing import Any
from typing import Any, Optional
import uuid

if TYPE_CHECKING:
    from app.hitl.approval_request import ApprovalRequest


# --- Consolidated from approval_capabilities.py ---
class ApprovalCapabilities(BaseModel):
    """Capabilities supported by an approval handler or system subsystem."""
    supports_escalation: bool = True
    supports_parallel_review: bool = False
    supports_timeout: bool = True
    supports_reassignment: bool = True
    supports_delegation: bool = True
    supports_quorum: bool = False
    supports_checkpoint_resume: bool = True
    supports_audit: bool = True

# --- Consolidated from approval_constraints.py ---
class ApprovalConstraints(BaseModel):
    """Boundary constraints governing human review and approval evaluation."""
    max_reviewers: int = 5
    minimum_reviewers: int = 1
    timeout: float = 3600.0
    quorum: int = 1
    allow_self_approval: bool = False
    allow_reassignment: bool = True
    allow_parallel_review: bool = False

# --- Consolidated from approval_metadata.py ---
class ApprovalMetadata(BaseModel):
    """Metadata attached to an approval request record."""
    version: str = '1.0.0'
    schema_version: str = '1.0'
    creator: str = 'system'
    priority: ApprovalPriority = ApprovalPriority.NORMAL
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ''
    tags: list[str] = Field(default_factory=list)

# --- Consolidated from approval_context.py ---
class ApprovalContext(BaseModel):
    """Runtime context tracking state during human review operations."""
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: str
    checkpoint_id: Optional[uuid.UUID] = None
    correlation_id: Optional[uuid.UUID] = None
    current_step: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from approval_event.py ---
class ApprovalEvent(BaseModel):
    """Event DTO placeholder representing human-in-the-loop lifecycle notifications."""
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str = 'approval_created'
    approval_id: uuid.UUID
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from approval_policy.py ---
class ApprovalPolicy(BaseModel):
    """Policies governing approval evaluation, required reviewer roles, timeouts, and escalation."""
    auto_expire: bool = True
    escalation_enabled: bool = True
    required_roles: list[HumanRole] = Field(default_factory=lambda: [HumanRole.APPROVER])
    approval_timeout: float = 86400.0
    max_reviewers: int = 5
    quorum_required: int = 1
    allow_reassignment: bool = True

# --- Consolidated from approval_result.py ---
class ApprovalResult(BaseModel):
    """Outcome container summarizing approval manager operations and decision evaluation."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    success: bool = True
    approval_request: Optional[ApprovalRequest] = None
    decision: ApprovalDecision = ApprovalDecision.NONE
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    processing_time: float = 0.0

# --- Consolidated from approval_snapshot.py ---
class ApprovalSnapshot(BaseModel):
    """Lightweight state snapshot of an approval request for auditing and replay inspection."""
    snapshot_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    approval_id: uuid.UUID
    status: ApprovalStatus
    decision: ApprovalDecision
    history: list[dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Consolidated from governance.py ---
class GovernancePolicy(BaseModel):
    """Reusable governance policy enforcing separation of duties, minimum reviewers, and audit rules."""
    approval_required: bool = True
    minimum_reviewers: int = 1
    separation_of_duties: bool = True
    escalation_rules: list[str] = Field(default_factory=lambda: ['timeout -> escalate_to_admin'])
    audit_required: bool = True

    def validate_decision(self, requester: str, reviewer: str) -> bool:
        """Validates decision compliance against separation of duties rule."""
        if self.separation_of_duties and requester == reviewer:
            raise GovernanceException(f"Separation of duties violation: Requester '{requester}' cannot approve their own request.")
        return True

