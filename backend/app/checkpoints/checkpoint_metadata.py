from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.checkpoints.checkpoint_version import CheckpointVersion


class CheckpointMetadata(BaseModel):
    """Descriptive metadata attached to a checkpoint record."""

    creator: str = "system"
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    version: CheckpointVersion = Field(default_factory=CheckpointVersion)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
