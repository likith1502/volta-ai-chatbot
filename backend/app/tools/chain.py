import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.tools.result import ToolResult


class ToolChainStep(BaseModel):
    """Single step in a sequential ToolChain."""

    step_id: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    output_key: Optional[str] = None


class ChainResult(BaseModel):
    """Output container for ToolChain execution."""

    chain_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    status: str = Field(default="success")
    success: bool = True
    completed_steps: int = Field(default=0, ge=0)
    total_steps: int = Field(default=0, ge=0)
    step_results: list[ToolResult] = Field(default_factory=list)
    total_latency_ms: float = Field(default=0.0, ge=0.0)
    final_output: Any = None


class ToolChain(BaseModel):
    """Sequential tool execution chain feeding output of step N into input of step N+1."""

    chain_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    steps: list[ToolChainStep] = Field(default_factory=list)
