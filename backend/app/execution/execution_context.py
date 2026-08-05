import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.context.types import ExecutionMode


class ExecutionContext(BaseModel):
    """Dynamic context tracked throughout graph execution traversal."""

    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    graph_id: str = ""
    workflow_id: Optional[str] = None
    current_node: Optional[str] = None
    previous_node: Optional[str] = None
    current_depth: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    execution_mode: ExecutionMode = ExecutionMode.ASYNC
    retry_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
