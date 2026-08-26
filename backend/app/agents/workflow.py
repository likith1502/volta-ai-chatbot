import uuid

from pydantic import BaseModel, Field

from app.agents.execution_mode import ExecutionMode


class MultiAgentWorkflow(BaseModel):
    """Workflow topology definition for a multi-agent team."""

    workflow_id: str = Field(default_factory=lambda: f"ma_wf_{uuid.uuid4().hex[:8]}")
    name: str = Field(..., min_length=1)
    team_id: str
    execution_mode: ExecutionMode = ExecutionMode.SUPERVISED
    step_sequence: list[str] = Field(
        default_factory=lambda: [
            "planner_agent",
            "research_agent",
            "tool_agent",
            "reviewer_agent",
            "supervisor_agent",
        ]
    )
