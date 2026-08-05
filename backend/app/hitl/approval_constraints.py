from pydantic import BaseModel


class ApprovalConstraints(BaseModel):
    """Boundary constraints governing human review and approval evaluation."""

    max_reviewers: int = 5
    minimum_reviewers: int = 1
    timeout: float = 3600.0
    quorum: int = 1
    allow_self_approval: bool = False
    allow_reassignment: bool = True
    allow_parallel_review: bool = False
