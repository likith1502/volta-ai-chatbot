import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.checkpoints.checkpoint_status import ReplayAction


class ReplayHistoryRecord(BaseModel):
    """Single historical entry recording a replay action on a checkpoint."""

    record_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    checkpoint_id: uuid.UUID
    action: ReplayAction
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReplayHistory(BaseModel):
    """Immutable log of replay actions and visited checkpoints during a replay session."""

    replay_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    records: list[ReplayHistoryRecord] = Field(default_factory=list)

    def record_action(
        self,
        checkpoint_id: uuid.UUID,
        action: ReplayAction,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ReplayHistoryRecord:
        """Records a new replay action into the history log."""
        rec = ReplayHistoryRecord(
            checkpoint_id=checkpoint_id,
            action=action,
            metadata=metadata or {},
        )
        self.records.append(rec)
        return rec
