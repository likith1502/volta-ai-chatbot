import uuid
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enum."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentTask(BaseModel):
    """Task payload assigned to an agent instance."""

    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    title: str = Field(..., min_length=1)
    description: str = Field(default="")
    assigned_agent_id: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=10)
    status: TaskStatus = TaskStatus.PENDING
    inputs: dict[str, Any] = Field(default_factory=dict)
    parent_task_id: Optional[str] = None


class TaskResult(BaseModel):
    """Output result produced upon completing an AgentTask."""

    task_id: str
    assigned_agent_id: str
    status: TaskStatus = TaskStatus.COMPLETED
    output: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = Field(default=0.0, ge=0.0)
    error_message: Optional[str] = None
