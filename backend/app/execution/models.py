"""Consolidated Models Module for Execution Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from app.context.types import ExecutionMode
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel
from pydantic import BaseModel, Field
from typing import Any, Optional
import uuid

# --- Consolidated from execution_status.py ---
class ExecutionStatus(str, Enum):
    """Lifecycle status of a graph execution lifecycle."""
    CREATED = 'created'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    PAUSED = 'paused'
    TIMEOUT = 'timeout'

# --- Consolidated from execution_policy.py ---
class ExecutionPolicy(BaseModel):
    """Configuration rules controlling graph execution behavior."""
    stop_on_error: bool = True
    continue_on_warning: bool = True
    allow_cycles: bool = False
    max_depth: int = 50
    max_execution_time: float = 60.0
    collect_metrics: bool = True
    emit_events: bool = True

# --- Consolidated from execution_context.py ---
class ExecutionContext(BaseModel):
    """Dynamic context tracked throughout graph execution traversal."""
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    graph_id: str = ''
    workflow_id: Optional[str] = None
    current_node: Optional[str] = None
    previous_node: Optional[str] = None
    current_depth: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    execution_mode: ExecutionMode = ExecutionMode.ASYNC
    retry_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

