from enum import Enum


class ApprovalStatus(str, Enum):
    """Lifecycle states of a human approval request."""

    CREATED = "created"
    PENDING = "pending"
    ASSIGNED = "assigned"
    WAITING = "waiting"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    ESCALATED = "escalated"
    COMPLETED = "completed"


class ApprovalPriority(str, Enum):
    """Priority levels for human approval requests."""

    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class ApprovalDecision(str, Enum):
    """Explicit human approval decision choices."""

    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    ESCALATE = "escalate"
    CANCEL = "cancel"
    DEFER = "defer"
    NONE = "none"


class HumanRole(str, Enum):
    """Role classification for human participants in review workflows."""

    REVIEWER = "reviewer"
    APPROVER = "approver"
    ADMIN = "admin"
    AUDITOR = "auditor"
    OBSERVER = "observer"
    OPERATOR = "operator"
    SYSTEM = "system"
