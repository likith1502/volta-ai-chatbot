import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.checkpoints.checkpoint_status import ReplayMode


class ReplayContext(BaseModel):
    """Runtime context tracking state and options during execution replay operations."""

    replay_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: Optional[uuid.UUID] = None
    checkpoint_id: Optional[uuid.UUID] = None
    current_step: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    replay_mode: ReplayMode = ReplayMode.FULL
    metadata: dict[str, Any] = Field(default_factory=dict)
