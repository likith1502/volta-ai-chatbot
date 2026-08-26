from typing import Any, Optional

from pydantic import BaseModel, Field

from app.prompt.context import PromptContext
from app.prompt.contracts import PromptResponse
from app.prompt.metrics import PromptMetrics
from app.prompt.trace import PromptTrace
from app.runtime.result import RuntimeResult


class PromptResult(BaseModel):
    """Unified result container mirroring Phase 6 and 7.0 Result containers."""

    rendered_prompt: Optional[PromptResponse] = None
    metrics: PromptMetrics = Field(default_factory=PromptMetrics)
    context: PromptContext
    trace: PromptTrace = Field(default_factory=PromptTrace)
    execution_status: str = Field(
        default="COMPLETED", description="'COMPLETED', 'FAILED', 'DEGRADED'"
    )
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    runtime_result: Optional[RuntimeResult] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
