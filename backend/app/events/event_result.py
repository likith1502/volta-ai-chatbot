from typing import Any

from pydantic import BaseModel, Field


class WorkflowEventResult(BaseModel):
    """Container summarizing the processing outcome of an event dispatch cycle."""

    success: bool = True
    processed: int = 0
    ignored: int = 0
    listener_count: int = 0
    processing_time: float = 0.0
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
