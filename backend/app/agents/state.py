from typing import Any
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Internal state storage for agent instances."""

    variables: dict[str, Any] = Field(default_factory=dict)
    execution_history: list[str] = Field(default_factory=list)
    output_history: list[dict[str, Any]] = Field(default_factory=list)
