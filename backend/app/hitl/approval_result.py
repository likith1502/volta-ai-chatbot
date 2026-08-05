from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.hitl.approval_request import ApprovalRequest
from app.hitl.approval_status import ApprovalDecision


class ApprovalResult(BaseModel):
    """Outcome container summarizing approval manager operations and decision evaluation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = True
    approval_request: Optional[ApprovalRequest] = None
    decision: ApprovalDecision = ApprovalDecision.NONE
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    processing_time: float = 0.0
