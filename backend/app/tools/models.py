"""Consolidated Models Module for Tools Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional
from typing import Optional
import uuid

# --- Consolidated from permission.py ---
class ToolPermission(str, Enum):
    """Authorization permission levels required to execute tools."""
    ALLOW = 'allow'
    DENY = 'deny'
    READONLY = 'readonly'
    ADMIN = 'admin'

# --- Consolidated from status.py ---
class ToolStatus(str, Enum):
    """Lifecycle status states for registered tools."""
    ACTIVE = 'active'
    DEPRECATED = 'deprecated'
    DISABLED = 'disabled'
    ERROR = 'error'

# --- Consolidated from type.py ---
class ToolType(str, Enum):
    """Categorical classification types for tools."""
    SYSTEM = 'system'
    UTILITY = 'utility'
    MATH = 'math'
    TIME = 'time'
    TEXT = 'text'
    FILE = 'file'
    NETWORK = 'network'
    SEARCH = 'search'
    CUSTOM = 'custom'

# --- Consolidated from capabilities.py ---
class ToolCapabilities(BaseModel):
    """Capability flags defining supported execution features of a tool."""
    supports_async: bool = True
    supports_streaming: bool = False
    supports_batch: bool = True
    supports_pipeline: bool = True
    supports_chain: bool = True

# --- Consolidated from context.py ---
class ToolContext(BaseModel):
    """Runtime execution context passed into tool execution handlers."""
    conversation_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None
    memory_context: Optional[dict[str, Any]] = None
    runtime_context: Optional[dict[str, Any]] = None
    prompt_context: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from manifest.py ---
class ToolManifest(BaseModel):
    """Complete tool packaging manifest containing schema, permissions, capabilities, and deprecation metadata."""
    tool_name: str = Field(..., min_length=1)
    version: str = '1.0.0'
    schema_spec: ToolSchema
    required_permission: ToolPermission = Field(default=ToolPermission.ALLOW)
    capabilities: ToolCapabilities = Field(default_factory=ToolCapabilities)
    examples: list[dict[str, Any]] = Field(default_factory=list)
    deprecated: bool = False
    replacement_tool: Optional[str] = None

# --- Consolidated from metadata.py ---
class ToolMetadata(BaseModel):
    """Metadata container for tool elements."""
    version: str = '1.0.0'
    author: str = 'system'
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    custom_attributes: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from policy.py ---
class ToolPolicy(BaseModel):
    """Execution policy engine settings enforcing timeouts, retries, and concurrency limits."""
    timeout_seconds: float = Field(default=10.0, ge=0.1)
    max_retries: int = Field(default=0, ge=0)
    concurrency_limit: int = Field(default=10, ge=1)
    rate_limit_per_minute: int = Field(default=60, ge=1)
    allow_sandbox_eval: bool = True

# --- Consolidated from request.py ---
class ToolRequest(BaseModel):
    """Immutable tool execution request payload."""
    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: Optional[uuid.UUID] = None
    conversation_id: Optional[uuid.UUID] = None
    tool_name: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from result.py ---
class ToolResult(BaseModel):
    """Immutable tool execution output container."""
    result_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    execution_id: Optional[uuid.UUID] = None
    tool_id: Optional[uuid.UUID] = None
    tool_name: str = Field(..., min_length=1)
    status: str = Field(default='success', description="'success', 'failed', 'error', 'timed_out', 'skipped'")
    success: bool = True
    output: Any = None
    execution_time_ms: float = Field(default=0.0, ge=0.0)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from schema.py ---
class ToolSchema(BaseModel):
    """Structural schema specification contract defining JSON input/output parameters and examples."""
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    input_schema: dict[str, Any] = Field(default_factory=dict, description='JSON Schema dict for parameters')
    output_schema: dict[str, Any] = Field(default_factory=dict, description='JSON Schema dict for returns')
    examples: list[dict[str, Any]] = Field(default_factory=list)
    version: str = '1.0.0'

# --- Consolidated from selector.py ---
class ToolSelector:
    """Selects best tool manifests based on name or tag match."""

    def select(self, manifests: list[ToolManifest], name: str) -> Optional[ToolManifest]:
        name_lower = name.strip().lower()
        for m in manifests:
            if m.tool_name.lower() == name_lower:
                return m
        return None

