from pydantic import BaseModel


class CheckpointPolicy(BaseModel):
    """Rules and retention policies governing automated and manual checkpoint creation."""

    auto_checkpoint: bool = True
    manual_checkpoint: bool = True
    checkpoint_interval: int = 1
    retain_latest: int = 10
    max_checkpoints: int = 50
    compression_enabled: bool = False
    validation_required: bool = True
