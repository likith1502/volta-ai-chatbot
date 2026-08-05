import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.context.state import ConversationState
from app.execution.execution_context import ExecutionContext
from app.workflow.metadata import NodeResult


class ExecutionSnapshot(BaseModel):
    """Immutable state and telemetry snapshot captured at a node step during traversal."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    snapshot_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    node_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    state: ConversationState
    node_result: Optional[NodeResult] = None
    execution_context: Optional[ExecutionContext] = None
