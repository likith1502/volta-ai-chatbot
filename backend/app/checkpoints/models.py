"""Consolidated Models Module for Checkpoints Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from app.checkpoints.checkpoint_status import ReplayMode
from app.execution.models import ExecutionContext
from datetime import datetime, timezone
from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Any, Optional
import uuid

# --- Consolidated from checkpoint_version.py ---
class CheckpointVersion(BaseModel):
    """Versioning specifications for checkpoint schemas, state models, and graphs."""
    checkpoint_version: str = '1.0.0'
    schema_version: str = '1.0'
    state_version: str = '1.0'
    execution_version: str = '1.0'
    graph_version: str = '1.0'

# --- Consolidated from checkpoint_metadata.py ---
class CheckpointMetadata(BaseModel):
    """Descriptive metadata attached to a checkpoint record."""
    creator: str = 'system'
    description: str = ''
    tags: list[str] = Field(default_factory=list)
    version: CheckpointVersion = Field(default_factory=CheckpointVersion)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Consolidated from checkpoint_policy.py ---
class CheckpointPolicy(BaseModel):
    """Rules and retention policies governing automated and manual checkpoint creation."""
    auto_checkpoint: bool = True
    manual_checkpoint: bool = True
    checkpoint_interval: int = 1
    retain_latest: int = 10
    max_checkpoints: int = 50
    compression_enabled: bool = False
    validation_required: bool = True

# --- Consolidated from checkpoint_validation.py ---
class CheckpointValidationResult(BaseModel):
    """Rich container summarizing checkpoint validation diagnostic results."""
    is_valid: bool = True
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    version_match: bool = True
    integrity_passed: bool = True
    compatible: bool = True

# --- Consolidated from replay_context.py ---
class ReplayContext(BaseModel):
    """Runtime context tracking state and options during execution replay operations."""
    replay_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: Optional[uuid.UUID] = None
    checkpoint_id: Optional[uuid.UUID] = None
    current_step: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    replay_mode: ReplayMode = ReplayMode.FULL
    metadata: dict[str, Any] = Field(default_factory=dict)

