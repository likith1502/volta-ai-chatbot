import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.hitl.approval_constraints import ApprovalConstraints
from app.hitl.approval_metadata import ApprovalMetadata
from app.hitl.approval_status import ApprovalDecision, ApprovalStatus


class ApprovalRequest(BaseModel):
    """
    Immutable human approval request model representing an execution gate.
    Approval requests are strictly frozen and read-only upon instantiation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    approval_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: str
    graph_id: str
    node_id: str
    checkpoint_id: Optional[uuid.UUID] = None
    requester: str = "system"
    assignee: Optional[str] = None
    status: ApprovalStatus = ApprovalStatus.CREATED
    decision: ApprovalDecision = ApprovalDecision.NONE
    reason: Optional[str] = None
    deadline: Optional[datetime] = None
    constraints: ApprovalConstraints = Field(default_factory=ApprovalConstraints)
    metadata: ApprovalMetadata = Field(default_factory=ApprovalMetadata)
