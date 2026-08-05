import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.hitl.approval_constraints import ApprovalConstraints
from app.hitl.approval_history import ApprovalHistory
from app.hitl.approval_metadata import ApprovalMetadata
from app.hitl.approval_request import ApprovalRequest
from app.hitl.approval_result import ApprovalResult
from app.hitl.approval_status import ApprovalDecision, ApprovalStatus, HumanRole
from app.hitl.exceptions import ApprovalAlreadyResolvedException, ApprovalNotFoundException


class ApprovalManager:
    """
    Manager governing the lifecycle, decisions, assignments, and state transitions
    of human approval gate requests.
    """

    def __init__(self) -> None:
        self._requests: Dict[uuid.UUID, ApprovalRequest] = {}
        self.history = ApprovalHistory()

    def create_request(
        self,
        workflow_id: str,
        graph_id: str,
        node_id: str,
        execution_id: Optional[uuid.UUID] = None,
        checkpoint_id: Optional[uuid.UUID] = None,
        assignee: Optional[str] = None,
        requester: str = "system",
        deadline: Optional[datetime] = None,
        constraints: Optional[ApprovalConstraints] = None,
        metadata: Optional[ApprovalMetadata] = None,
    ) -> ApprovalRequest:
        """Creates and stores a new ApprovalRequest instance in PENDING or ASSIGNED status."""
        status = ApprovalStatus.ASSIGNED if assignee else ApprovalStatus.PENDING
        req = ApprovalRequest(
            execution_id=execution_id or uuid.uuid4(),
            workflow_id=workflow_id,
            graph_id=graph_id,
            node_id=node_id,
            checkpoint_id=checkpoint_id,
            requester=requester,
            assignee=assignee,
            status=status,
            decision=ApprovalDecision.NONE,
            deadline=deadline,
            constraints=constraints or ApprovalConstraints(),
            metadata=metadata or ApprovalMetadata(),
        )
        self._requests[req.approval_id] = req
        return req

    def get_request(self, approval_id: uuid.UUID) -> ApprovalRequest:
        """Retrieves an ApprovalRequest by ID."""
        if approval_id not in self._requests:
            raise ApprovalNotFoundException(f"Approval request '{approval_id}' not found.")
        return self._requests[approval_id]

    def _ensure_active(self, req: ApprovalRequest) -> None:
        """Verifies that an approval request has not already been resolved."""
        resolved_statuses = {
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
            ApprovalStatus.CANCELLED,
            ApprovalStatus.EXPIRED,
            ApprovalStatus.COMPLETED,
        }
        if req.status in resolved_statuses:
            raise ApprovalAlreadyResolvedException(
                f"Approval request '{req.approval_id}' is already resolved with status '{req.status.value}'."
            )

    def assign(self, approval_id: uuid.UUID, assignee: str) -> ApprovalRequest:
        """Assigns an approval request to a specified reviewer."""
        existing = self.get_request(approval_id)
        self._ensure_active(existing)

        updated = ApprovalRequest(
            approval_id=existing.approval_id,
            execution_id=existing.execution_id,
            workflow_id=existing.workflow_id,
            graph_id=existing.graph_id,
            node_id=existing.node_id,
            checkpoint_id=existing.checkpoint_id,
            requester=existing.requester,
            assignee=assignee,
            status=ApprovalStatus.ASSIGNED,
            decision=existing.decision,
            reason=existing.reason,
            deadline=existing.deadline,
            constraints=existing.constraints,
            metadata=existing.metadata,
        )
        self._requests[approval_id] = updated
        return updated

    def approve(self, approval_id: uuid.UUID, reviewer: str, comments: Optional[str] = None) -> ApprovalRequest:
        """Approves an approval request."""
        existing = self.get_request(approval_id)
        self._ensure_active(existing)

        updated = ApprovalRequest(
            approval_id=existing.approval_id,
            execution_id=existing.execution_id,
            workflow_id=existing.workflow_id,
            graph_id=existing.graph_id,
            node_id=existing.node_id,
            checkpoint_id=existing.checkpoint_id,
            requester=existing.requester,
            assignee=existing.assignee or reviewer,
            status=ApprovalStatus.APPROVED,
            decision=ApprovalDecision.APPROVE,
            reason=comments,
            deadline=existing.deadline,
            constraints=existing.constraints,
            metadata=existing.metadata,
        )
        self._requests[approval_id] = updated
        self.history.record_decision(
            approval_id=approval_id,
            reviewer=reviewer,
            decision=ApprovalDecision.APPROVE,
            role=HumanRole.APPROVER,
            comments=comments,
        )
        return updated

    def reject(self, approval_id: uuid.UUID, reviewer: str, reason: Optional[str] = None) -> ApprovalRequest:
        """Rejects an approval request."""
        existing = self.get_request(approval_id)
        self._ensure_active(existing)

        updated = ApprovalRequest(
            approval_id=existing.approval_id,
            execution_id=existing.execution_id,
            workflow_id=existing.workflow_id,
            graph_id=existing.graph_id,
            node_id=existing.node_id,
            checkpoint_id=existing.checkpoint_id,
            requester=existing.requester,
            assignee=existing.assignee or reviewer,
            status=ApprovalStatus.REJECTED,
            decision=ApprovalDecision.REJECT,
            reason=reason,
            deadline=existing.deadline,
            constraints=existing.constraints,
            metadata=existing.metadata,
        )
        self._requests[approval_id] = updated
        self.history.record_decision(
            approval_id=approval_id,
            reviewer=reviewer,
            decision=ApprovalDecision.REJECT,
            role=HumanRole.APPROVER,
            comments=reason,
        )
        return updated

    def escalate(self, approval_id: uuid.UUID, reviewer: str, reason: Optional[str] = None) -> ApprovalRequest:
        """Escalates an approval request to higher governance."""
        existing = self.get_request(approval_id)
        self._ensure_active(existing)

        updated = ApprovalRequest(
            approval_id=existing.approval_id,
            execution_id=existing.execution_id,
            workflow_id=existing.workflow_id,
            graph_id=existing.graph_id,
            node_id=existing.node_id,
            checkpoint_id=existing.checkpoint_id,
            requester=existing.requester,
            assignee=existing.assignee,
            status=ApprovalStatus.ESCALATED,
            decision=ApprovalDecision.ESCALATE,
            reason=reason,
            deadline=existing.deadline,
            constraints=existing.constraints,
            metadata=existing.metadata,
        )
        self._requests[approval_id] = updated
        self.history.record_decision(
            approval_id=approval_id,
            reviewer=reviewer,
            decision=ApprovalDecision.ESCALATE,
            role=HumanRole.ADMIN,
            comments=reason,
        )
        return updated

    def expire(self, approval_id: uuid.UUID) -> ApprovalRequest:
        """Expires an unhandled approval request."""
        existing = self.get_request(approval_id)
        self._ensure_active(existing)

        updated = ApprovalRequest(
            approval_id=existing.approval_id,
            execution_id=existing.execution_id,
            workflow_id=existing.workflow_id,
            graph_id=existing.graph_id,
            node_id=existing.node_id,
            checkpoint_id=existing.checkpoint_id,
            requester=existing.requester,
            assignee=existing.assignee,
            status=ApprovalStatus.EXPIRED,
            decision=ApprovalDecision.NONE,
            reason="Deadline expired",
            deadline=existing.deadline,
            constraints=existing.constraints,
            metadata=existing.metadata,
        )
        self._requests[approval_id] = updated
        return updated

    def cancel(self, approval_id: uuid.UUID, reason: Optional[str] = None) -> ApprovalRequest:
        """Cancels an approval request."""
        existing = self.get_request(approval_id)
        self._ensure_active(existing)

        updated = ApprovalRequest(
            approval_id=existing.approval_id,
            execution_id=existing.execution_id,
            workflow_id=existing.workflow_id,
            graph_id=existing.graph_id,
            node_id=existing.node_id,
            checkpoint_id=existing.checkpoint_id,
            requester=existing.requester,
            assignee=existing.assignee,
            status=ApprovalStatus.CANCELLED,
            decision=ApprovalDecision.CANCEL,
            reason=reason,
            deadline=existing.deadline,
            constraints=existing.constraints,
            metadata=existing.metadata,
        )
        self._requests[approval_id] = updated
        return updated

    def complete(self, approval_id: uuid.UUID) -> ApprovalRequest:
        """Marks an approved/rejected request as COMPLETED."""
        existing = self.get_request(approval_id)
        updated = ApprovalRequest(
            approval_id=existing.approval_id,
            execution_id=existing.execution_id,
            workflow_id=existing.workflow_id,
            graph_id=existing.graph_id,
            node_id=existing.node_id,
            checkpoint_id=existing.checkpoint_id,
            requester=existing.requester,
            assignee=existing.assignee,
            status=ApprovalStatus.COMPLETED,
            decision=existing.decision,
            reason=existing.reason,
            deadline=existing.deadline,
            constraints=existing.constraints,
            metadata=existing.metadata,
        )
        self._requests[approval_id] = updated
        return updated
