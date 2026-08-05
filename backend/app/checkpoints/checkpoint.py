import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.checkpoints.checkpoint_metadata import CheckpointMetadata
from app.checkpoints.checkpoint_status import CheckpointStatus
from app.context.state import ConversationState
from app.execution.execution_snapshot import ExecutionSnapshot


class Checkpoint(BaseModel):
    """
    Immutable session checkpoint snapshot storing execution state lineage.
    Checkpoints are strictly read-only and never mutated in-place once created.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    checkpoint_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: str
    graph_id: str
    state_snapshot: ConversationState
    execution_snapshot: Optional[ExecutionSnapshot] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: CheckpointStatus = CheckpointStatus.CREATED
    metadata: CheckpointMetadata = Field(default_factory=CheckpointMetadata)
