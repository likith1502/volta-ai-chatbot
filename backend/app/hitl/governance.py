from pydantic import BaseModel, Field

from app.hitl.exceptions import GovernanceError


class GovernancePolicy(BaseModel):
    """Reusable governance policy enforcing separation of duties, minimum reviewers, and audit rules."""

    approval_required: bool = True
    minimum_reviewers: int = 1
    separation_of_duties: bool = True
    escalation_rules: list[str] = Field(
        default_factory=lambda: ["timeout -> escalate_to_admin"]
    )
    audit_required: bool = True

    def validate_decision(self, requester: str, reviewer: str) -> bool:
        """Validates decision compliance against separation of duties rule."""
        if self.separation_of_duties and requester == reviewer:
            raise GovernanceError(
                f"Separation of duties violation: Requester '{requester}' cannot approve their own request."
            )
        return True
