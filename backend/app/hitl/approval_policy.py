from pydantic import BaseModel, Field

from app.hitl.approval_status import HumanRole


class ApprovalPolicy(BaseModel):
    """Policies governing approval evaluation, required reviewer roles, timeouts, and escalation."""

    auto_expire: bool = True
    escalation_enabled: bool = True
    required_roles: list[HumanRole] = Field(
        default_factory=lambda: [HumanRole.APPROVER]
    )
    approval_timeout: float = 86400.0
    max_reviewers: int = 5
    quorum_required: int = 1
    allow_reassignment: bool = True
