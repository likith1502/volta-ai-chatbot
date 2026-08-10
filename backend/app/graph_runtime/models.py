"""Consolidated Models Module for Graph_Runtime Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from app.graph_runtime.retry import RetryPolicy
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional
from typing import Optional
import uuid

# --- Consolidated from state.py ---
class GraphRuntimeState(str, Enum):
    """Execution lifecycle state for Graph Runtime sessions."""
    RUNNING = 'running'
    WAITING = 'waiting'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    INTERRUPTED = 'interrupted'

# --- Consolidated from transition.py ---
class GraphTransition(BaseModel):
    """Represents a state transition edge between two runtime graph nodes."""
    from_node: str
    to_node: str
    condition_key: Optional[str] = None
    is_executed: bool = False

# --- Consolidated from timeout.py ---
class TimeoutPolicy(BaseModel):
    """Timeout policies enforced per node, workflow, and total execution."""
    node_timeout_seconds: float = Field(default=10.0, ge=0.1)
    workflow_timeout_seconds: float = Field(default=60.0, ge=1.0)
    execution_timeout_seconds: float = Field(default=120.0, ge=1.0)

# --- Consolidated from capabilities.py ---
class GraphRuntimeCapabilities(BaseModel):
    """Capabilities supported by Graph Runtime Engine."""
    supports_dag_planning: bool = True
    supports_conditional_routing: bool = True
    supports_parallel_nodes: bool = True
    supports_auto_checkpointing: bool = True
    supports_hitl_interrupts: bool = True
    supports_realtime_streaming: bool = True

# --- Consolidated from config.py ---
class GraphRuntimeConfig(BaseModel):
    """Configuration settings for Graph Runtime Engine."""
    max_execution_steps: int = Field(default=50, ge=1)
    enable_parallel_execution: bool = True
    enable_auto_checkpoint: bool = True
    checkpoint_interval_steps: int = Field(default=5, ge=1)
    default_timeout_seconds: float = Field(default=30.0, ge=0.5)
    enable_streaming: bool = True
    enable_hitl: bool = True

# --- Consolidated from context.py ---
class GraphRuntimeContext(BaseModel):
    """Runtime execution context aggregating conversation state across workflow execution."""
    conversation_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: str = 'default_workflow'
    state_data: dict[str, Any] = Field(default_factory=dict)
    memory_context: Optional[dict[str, Any]] = None
    prompt_context: Optional[dict[str, Any]] = None
    tool_context: Optional[dict[str, Any]] = None
    runtime_context: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from node_context.py ---
class NodeExecutionContext(BaseModel):
    """Context snapshot captured for a single node execution turn."""
    node_id: str
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    inputs: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    memory_snapshot: Optional[dict[str, Any]] = None
    tool_snapshot: Optional[dict[str, Any]] = None
    runtime_snapshot: Optional[dict[str, Any]] = None
    prompt_snapshot: Optional[dict[str, Any]] = None

# --- Consolidated from policy.py ---
class GraphRuntimePolicy(BaseModel):
    """Centralized runtime execution policies combining retry, timeout, parallelism, and streaming settings."""
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    timeout_policy: TimeoutPolicy = Field(default_factory=TimeoutPolicy)
    allow_parallel_nodes: bool = True
    checkpoint_interval: int = Field(default=5, ge=1)
    streaming_enabled: bool = True
    hitl_enabled: bool = True
    memory_injection_enabled: bool = True
    tool_execution_enabled: bool = True

# --- Consolidated from versioning.py ---
class GraphRuntimeVersion(BaseModel):
    """Version metadata container."""
    version: str = '7.4.0'
    milestone: str = 'Phase 7.4 Enterprise Graph Runtime Integration'
    frozen_dependencies: list[str] = Field(default_factory=lambda: ['app.runtime (v7.0)', 'app.prompt (v7.1)', 'app.memory (v7.2)', 'app.tools (v7.3)'])

