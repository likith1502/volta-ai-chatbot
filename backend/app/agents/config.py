from pydantic import BaseModel, Field


class AgentRuntimeConfig(BaseModel):
    """Global configuration settings for Enterprise Multi-Agent Orchestration Runtime."""

    max_agents: int = Field(default=100, ge=1)
    default_provider: str = "mock"
    default_model: str = "mock-model-v1"
    event_emission_enabled: bool = True
