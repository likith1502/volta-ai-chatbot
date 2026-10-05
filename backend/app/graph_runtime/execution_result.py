import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.graph_runtime.state import GraphRuntimeState
from app.graph_runtime.trace import ExecutionTrace


class GraphExecutionResult(BaseModel):
    """Immutable execution output container returned by GraphRuntimeExecutor."""

    result_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    session_id: Optional[uuid.UUID] = None
    workflow_id: str
    status: GraphRuntimeState = Field(default=GraphRuntimeState.COMPLETED)
    success: bool = True
    visited_nodes: list[str] = Field(default_factory=list)
    total_latency_ms: float = Field(default=0.0, ge=0.0)
    memory_stats: dict[str, Any] = Field(default_factory=dict)
    tool_stats: dict[str, Any] = Field(default_factory=dict)
    runtime_stats: dict[str, Any] = Field(default_factory=dict)
    token_usage: dict[str, int] = Field(default_factory=dict)
    final_output: Any = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    checkpoint_id: Optional[str] = None
    trace: Optional[ExecutionTrace] = None
