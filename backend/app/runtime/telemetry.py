"""Consolidated Telemetry Module for Runtime Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from app.runtime.context import RuntimeContext
from app.runtime.contracts import ChatMessage, RuntimeRequest, RuntimeResponse
from app.runtime.contracts import RuntimeResponse
from app.runtime.contracts import RuntimeResponse, RuntimeRequest
from app.runtime.contracts import RuntimeTokenUsage
from pydantic import BaseModel, Field
from typing import Any
from typing import Any, Optional
import json

# --- Consolidated from metrics.py ---
class RuntimeMetrics(BaseModel):
    """Execution telemetry container tracking latency, breakdown timings, token counts, and cost."""
    latency_ms: float = Field(default=0.0, ge=0.0, description='Total turn execution latency in milliseconds')
    provider_time_ms: float = Field(default=0.0, ge=0.0, description='Time spent awaiting remote LLM provider')
    serialization_time_ms: float = Field(default=0.0, ge=0.0, description='Time spent serializing request/response payload')
    total_execution_time_ms: float = Field(default=0.0, ge=0.0, description='Total wall-clock execution time')
    retries_attempted: int = Field(default=0, ge=0, description='Number of backoff retry attempts executed')
    tokens: RuntimeTokenUsage = Field(default_factory=RuntimeTokenUsage)
    estimated_cost_usd: float = Field(default=0.0, ge=0.0)

# --- Consolidated from serializer.py ---
class ConversationSerializer:
    """Serialization & export helper for runtime conversation turns, requests, and results."""

    @staticmethod
    def to_json(obj: Any) -> str:
        """Serializes runtime primitives (RuntimeRequest, RuntimeResponse, RuntimeResult) to JSON string."""
        if hasattr(obj, 'model_dump_json'):
            return obj.model_dump_json(indent=2)
        return json.dumps(obj, default=str, indent=2)

    @staticmethod
    def to_markdown(messages: list[ChatMessage], result: RuntimeResult) -> str:
        """Exports a conversation turn and runtime result to clean GitHub-flavored markdown."""
        lines = [f'# Runtime Turn Export — {result.context.runtime_id}', f'- **Provider**: `{result.context.provider}` | **Model**: `{result.context.model}`', f'- **Execution Status**: `{result.execution_status}`', f'- **Latency**: `{result.metrics.latency_ms:.2f}ms` | **Tokens**: `{result.metrics.tokens.total_tokens}` | **Est. Cost**: `${result.metrics.estimated_cost_usd:.6f}`', '', '## Messages']
        for msg in messages:
            role_header = f'### {msg.role.upper()}'
            lines.append(role_header)
            lines.append(msg.content)
            lines.append('')
        if result.response:
            lines.append('## Assistant Response')
            lines.append(result.response.content)
            lines.append('')
        return '\n'.join(lines)

# --- Consolidated from result.py ---
class RuntimeResult(BaseModel):
    """Unified runtime execution result container mirroring Phase 6 Result objects (ExecutionResult, ReplayResult, StreamResult, ApprovalResult)."""
    response: Optional[RuntimeResponse] = None
    metrics: RuntimeMetrics = Field(default_factory=RuntimeMetrics)
    context: RuntimeContext
    execution_status: str = Field(default='COMPLETED', description="'COMPLETED', 'FAILED', 'DEGRADED'")
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    runtime_version: str = '7.0.0'
    provider_version: str = '1.0.0'
    api_version: str = 'v1'
    metadata: dict[str, Any] = Field(default_factory=dict)

