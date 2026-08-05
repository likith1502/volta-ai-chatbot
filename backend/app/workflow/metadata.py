import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.context.state import ConversationState
from app.context.types import ExecutionMode, WorkflowStatus
from app.workflow.node_types import WorkflowNodeType


class NodeResult(BaseModel):
    """Contract model for node execution results in future graph execution engines."""

    state: Optional[ConversationState] = None
    status: WorkflowStatus = WorkflowStatus.COMPLETED
    next_node: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    execution_time: float = 0.0
    outputs: dict[str, Any] = Field(default_factory=dict)


class NodeCapability(BaseModel):
    """Metadata declaring functional capabilities supported by a workflow node."""

    supports_streaming: bool = False
    supports_retry: bool = True
    supports_parallel: bool = True
    supports_checkpoint: bool = True
    supports_human_review: bool = False
    supports_timeout: bool = True
    supports_cancellation: bool = True


class WorkflowNodeMetadata(BaseModel):
    """Metadata describing a workflow node definition."""

    author: str = "System"
    version: str = "1.0.0"
    api_version: str = "v1"
    schema_version: str = "1.0"
    tags: list[str] = Field(default_factory=list)
    description: str = ""
    category: WorkflowNodeType = WorkflowNodeType.CUSTOM
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    experimental: bool = False
    deprecated: bool = False


class WorkflowNodeConfig(BaseModel):
    """Runtime configuration control parameters for node execution."""

    timeout: float = 30.0
    retry_policy: dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3, "backoff": 1.5})
    parallel: bool = False
    checkpoint: bool = False
    cache: bool = False


class NodeExecutionConstraints(BaseModel):
    """Execution policy constraints for a workflow node."""

    max_execution_time: float = 60.0
    max_retries: int = 3
    retryable: bool = True
    interruptible: bool = True
    idempotent: bool = True


class NodeExecutionContext(BaseModel):
    """Runtime execution context contract passed into node lifecycle hooks."""

    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    graph_id: Optional[str] = None
    node_id: Optional[str] = None
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_mode: ExecutionMode = ExecutionMode.ASYNC
    retry_count: int = 0
    timeout: float = 30.0
