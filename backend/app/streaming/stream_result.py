from typing import Any

from pydantic import BaseModel, Field


class StreamResult(BaseModel):
    """Outcome container summarizing stream message dispatch and processing results."""

    success: bool = True
    delivered: int = 0
    skipped: int = 0
    warnings: list[str] = Field(default_factory=list)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    processing_time: float = 0.0
