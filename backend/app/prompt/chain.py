import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.prompt.result import PromptResult


class PromptStep(BaseModel):
    """Single step contract within a multi-step PromptChain (e.g. Planner -> Retriever -> Critic -> Reflection)."""

    step_id: str
    template_id: str
    description: Optional[str] = None
    input_mapping: dict[str, str] = Field(default_factory=dict)
    output_key: Optional[str] = None


class PromptChain(BaseModel):
    """Multi-step prompt execution chain representation preparing for Phase 7.5 Multi-Agent workflows."""

    chain_id: str
    display_name: str
    steps: list[PromptStep] = Field(default_factory=list)
    description: Optional[str] = None


class ChainResult(BaseModel):
    """Execution result container for a PromptChain execution."""

    chain_id: str
    execution_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    step_results: dict[str, PromptResult] = Field(default_factory=dict)
    final_output: Optional[str] = None
    execution_status: str = Field(default="COMPLETED")
    total_latency_ms: float = Field(default=0.0, ge=0.0)
