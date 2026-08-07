from pydantic import BaseModel, Field


class AgentCapabilities(BaseModel):
    """Capabilities supported by an agent."""

    supports_planning: bool = True
    supports_delegation: bool = True
    supports_tool_execution: bool = True
    supports_memory_access: bool = True
    supports_streaming: bool = True
    supports_hitl: bool = True
    supported_tools: list[str] = Field(default_factory=lambda: ["echo", "calculator", "datetime", "uuid"])
