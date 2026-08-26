from pydantic import BaseModel, Field


class TimeoutPolicy(BaseModel):
    """Timeout policies enforced per node, workflow, and total execution."""

    node_timeout_seconds: float = Field(default=10.0, ge=0.1)
    workflow_timeout_seconds: float = Field(default=60.0, ge=1.0)
    execution_timeout_seconds: float = Field(default=120.0, ge=1.0)
