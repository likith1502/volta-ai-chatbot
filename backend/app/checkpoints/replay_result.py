from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.context.state import ConversationState
from app.execution.execution_snapshot import ExecutionSnapshot


class ReplayResult(BaseModel):
    """Outcome container returned by execution replay runs."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = True
    final_state: Optional[ConversationState] = None
    visited_snapshots: list[ExecutionSnapshot] = Field(default_factory=list)
    execution_time: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
