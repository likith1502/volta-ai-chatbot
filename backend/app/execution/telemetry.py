"""Consolidated Telemetry Module for Execution Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from app.context.state import ConversationState
from app.execution.execution_context import ExecutionContext
from app.execution.execution_status import ExecutionStatus
from app.execution.models import ExecutionContext
from app.workflow.metadata import NodeResult
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field
from pydantic import BaseModel, Field
from typing import Any
from typing import Any, Optional
from typing import Optional
import uuid

# --- Consolidated from execution_metrics.py ---
class ExecutionMetrics(BaseModel):
    """Runtime statistics and metrics captured during graph execution."""
    execution_time: float = 0.0
    node_count: int = 0
    visited_nodes: list[str] = Field(default_factory=list)
    failed_nodes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    success_rate: float = 1.0

    def compute_success_rate(self) -> None:
        """Recalculates success rate based on visited and failed node counts."""
        if not self.visited_nodes:
            self.success_rate = 1.0
        else:
            successful = len(self.visited_nodes) - len(self.failed_nodes)
            self.success_rate = round(max(0.0, successful / len(self.visited_nodes)), 4)

# --- Consolidated from execution_result.py ---
class ExecutionResult(BaseModel):
    """Container representing the complete outcome of a graph execution run."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    final_state: Optional[ConversationState] = None
    visited_nodes: list[str] = Field(default_factory=list)
    execution_metrics: ExecutionMetrics = Field(default_factory=ExecutionMetrics)
    execution_status: ExecutionStatus = ExecutionStatus.COMPLETED
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    execution_context: Optional[ExecutionContext] = None
    snapshots: list[ExecutionSnapshot] = Field(default_factory=list)

# --- Consolidated from execution_snapshot.py ---
class ExecutionSnapshot(BaseModel):
    """Immutable state and telemetry snapshot captured at a node step during traversal."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    snapshot_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    node_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    state: ConversationState
    node_result: Optional[NodeResult] = None
    execution_context: Optional[ExecutionContext] = None

