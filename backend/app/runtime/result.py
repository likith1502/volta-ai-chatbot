from typing import Any, Optional

from pydantic import BaseModel, Field

from app.runtime.context import RuntimeContext
from app.runtime.contracts import RuntimeResponse
from app.runtime.metrics import RuntimeMetrics


class RuntimeResult(BaseModel):
    """Unified runtime execution result container mirroring Phase 6 Result objects (ExecutionResult, ReplayResult, StreamResult, ApprovalResult)."""

    response: Optional[RuntimeResponse] = None
    metrics: RuntimeMetrics = Field(default_factory=RuntimeMetrics)
    context: RuntimeContext
    execution_status: str = Field(
        default="COMPLETED", description="'COMPLETED', 'FAILED', 'DEGRADED'"
    )
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    runtime_version: str = "7.0.0"
    provider_version: str = "1.0.0"
    api_version: str = "v1"
    metadata: dict[str, Any] = Field(default_factory=dict)
