import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from app.graph_runtime.cursor import GraphCursor
from app.graph_runtime.state import GraphRuntimeState


class GraphRuntimeSession(BaseModel):
    """Session container tracking active Graph Runtime execution across multiple turns."""

    session_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: str = "default_workflow"
    state: GraphRuntimeState = Field(default=GraphRuntimeState.RUNNING)
    cursor: GraphCursor = Field(default_factory=GraphCursor)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    context_data: dict[str, Any] = Field(default_factory=dict)
    visited_history: list[str] = Field(default_factory=list)
