import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.checkpoints.checkpoint_metadata import CheckpointMetadata
from app.checkpoints.checkpoint_status import CheckpointStatus
from app.context.state import ConversationState
from app.execution.execution_snapshot import ExecutionSnapshot


_timestamp_lock = threading.Lock()
_last_timestamp: Optional[datetime] = None


def _next_timestamp() -> datetime:
    """Returns a UTC timestamp that is strictly later than any previously issued one.

    Coarse system clocks (notably on Windows) can hand out the same value to two
    checkpoints created moments apart, which made "latest checkpoint" lookups
    return an older state. Bumping by one microsecond keeps the order exact.
    """
    global _last_timestamp
    with _timestamp_lock:
        now = datetime.now(timezone.utc)
        if _last_timestamp is not None and now <= _last_timestamp:
            now = _last_timestamp + timedelta(microseconds=1)
        _last_timestamp = now
        return now


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
    timestamp: datetime = Field(default_factory=_next_timestamp)
    status: CheckpointStatus = CheckpointStatus.CREATED
    metadata: CheckpointMetadata = Field(default_factory=CheckpointMetadata)
