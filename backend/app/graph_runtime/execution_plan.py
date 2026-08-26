import uuid
from typing import Any

from pydantic import BaseModel, Field

from app.graph_runtime.policy import GraphRuntimePolicy


class GraphExecutionPlan(BaseModel):
    """Ordered execution DAG plan decoupling plan generation from execution scheduling."""

    plan_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    workflow_id: str
    execution_order: list[str] = Field(default_factory=list)
    parallel_groups: list[list[str]] = Field(default_factory=list)
    conditional_branches: dict[str, str] = Field(default_factory=dict)
    policy: GraphRuntimePolicy = Field(default_factory=GraphRuntimePolicy)
    metadata: dict[str, Any] = Field(default_factory=dict)
