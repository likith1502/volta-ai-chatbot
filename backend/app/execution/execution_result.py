from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.context.state import ConversationState
from app.execution.execution_context import ExecutionContext
from app.execution.execution_metrics import ExecutionMetrics
from app.execution.execution_snapshot import ExecutionSnapshot
from app.execution.execution_status import ExecutionStatus


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
