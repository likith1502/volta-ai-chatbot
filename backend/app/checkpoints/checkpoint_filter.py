import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.checkpoints.checkpoint import Checkpoint
from app.checkpoints.checkpoint_status import CheckpointStatus


class CheckpointFilter(BaseModel):
    """Predicate filter for matching checkpoint records against specified search criteria."""

    workflow_id: Optional[str] = None
    execution_id: Optional[uuid.UUID] = None
    graph_id: Optional[str] = None
    statuses: list[CheckpointStatus] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def matches(self, checkpoint: Checkpoint) -> bool:
        """Evaluates whether a checkpoint record satisfies all specified non-empty criteria."""
        if self.workflow_id and checkpoint.workflow_id != self.workflow_id:
            return False

        if self.execution_id and checkpoint.execution_id != self.execution_id:
            return False

        if self.graph_id and checkpoint.graph_id != self.graph_id:
            return False

        if self.statuses and checkpoint.status not in self.statuses:
            return False

        if self.tags:
            cp_tags = set(checkpoint.metadata.tags)
            if not any(tag in cp_tags for tag in self.tags):
                return False

        if self.start_time and checkpoint.timestamp < self.start_time:
            return False

        if self.end_time and checkpoint.timestamp > self.end_time:
            return False

        return True
