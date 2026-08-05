import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field


class ApprovalContext(BaseModel):
    """Runtime context tracking state during human review operations."""

    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: str
    checkpoint_id: Optional[uuid.UUID] = None
    correlation_id: Optional[uuid.UUID] = None
    current_step: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
