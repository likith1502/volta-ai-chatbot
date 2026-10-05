"""Consolidated Telemetry Module for Checkpoints Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from app.context.state import ConversationState
from app.execution.execution_snapshot import ExecutionSnapshot
from pydantic import BaseModel
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Optional

# --- Consolidated from replay_metrics.py ---
class ReplayMetrics(BaseModel):
    """Telemetry metrics captured during execution replay operations."""
    replayed_steps: int = 0
    replay_duration: float = 0.0
    recovery_time: float = 0.0
    checkpoint_count: int = 0
    success_rate: float = 1.0

    def compute_success_rate(self, failed_steps: int=0) -> None:
        """Calculates success rate metric."""
        total = self.replayed_steps + failed_steps
        if total == 0:
            self.success_rate = 1.0
        else:
            self.success_rate = round(max(0.0, self.replayed_steps / total), 4)

# --- Consolidated from replay_result.py ---
class ReplayResult(BaseModel):
    """Outcome container returned by execution replay runs."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    success: bool = True
    final_state: Optional[ConversationState] = None
    visited_snapshots: list[ExecutionSnapshot] = Field(default_factory=list)
    execution_time: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)

