import uuid
from typing import Optional

from app.checkpoints.checkpoint_manager import CheckpointManager
from app.context.state import ConversationState
from app.hitl.approval_manager import ApprovalManager
from app.hitl.approval_status import ApprovalDecision, ApprovalStatus
from app.hitl.exceptions import ResumeException


class ResumeManager:
    """Manager governing execution resume operations from human approval decisions or checkpoints."""

    def __init__(
        self,
        checkpoint_manager: Optional[CheckpointManager] = None,
        approval_manager: Optional[ApprovalManager] = None,
    ) -> None:
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()
        self.approval_manager = approval_manager or ApprovalManager()

    def resume_from_checkpoint(self, checkpoint_id: uuid.UUID) -> ConversationState:
        """Restores and returns state snapshot from specified checkpoint."""
        return self.checkpoint_manager.restore_checkpoint(checkpoint_id)

    def resume_from_approval(self, approval_id: uuid.UUID) -> ConversationState:
        """
        Validates that approval request was APPROVED and restores state snapshot
        from its associated checkpoint.
        """
        req = self.approval_manager.get_request(approval_id)
        if req.decision != ApprovalDecision.APPROVE and req.status not in (ApprovalStatus.APPROVED, ApprovalStatus.COMPLETED):
            raise ResumeException(
                f"Cannot resume execution from approval '{approval_id}': status is '{req.status.value}', decision is '{req.decision.value}'."
            )

        if not req.checkpoint_id:
            raise ResumeException(f"Approval request '{approval_id}' has no associated checkpoint_id to resume from.")

        return self.checkpoint_manager.restore_checkpoint(req.checkpoint_id)

    def restart_execution(self, workflow_id: str) -> ConversationState:
        """Restores earliest state snapshot for specified workflow_id."""
        cps = self.checkpoint_manager.list_checkpoints()
        wf_cps = [c for c in cps if c.workflow_id == workflow_id]
        if not wf_cps:
            raise ResumeException(f"No checkpoints found for workflow '{workflow_id}' to restart.")
        earliest = min(wf_cps, key=lambda c: c.timestamp)
        return earliest.state_snapshot
