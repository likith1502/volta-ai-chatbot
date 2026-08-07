import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field


class PlannerResult(BaseModel):
    """Output evaluation container produced by GraphPlanner."""

    plan_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: str
    target_nodes: list[str] = Field(default_factory=list)
    initial_node: str = "START"
    is_valid: bool = True
    estimated_steps: int = Field(default=1, ge=1)
    routing_metadata: dict[str, Any] = Field(default_factory=dict)
