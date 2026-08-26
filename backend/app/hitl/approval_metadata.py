from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.hitl.approval_status import ApprovalPriority


class ApprovalMetadata(BaseModel):
    """Metadata attached to an approval request record."""

    version: str = "1.0.0"
    schema_version: str = "1.0"
    creator: str = "system"
    priority: ApprovalPriority = ApprovalPriority.NORMAL
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str = ""
    tags: list[str] = Field(default_factory=list)
