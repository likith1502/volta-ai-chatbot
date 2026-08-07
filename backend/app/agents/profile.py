from pydantic import BaseModel, Field


class AgentProfile(BaseModel):
    """Prompt and LLM generation profile linking to Prompt Execution Engine (v7.1)."""

    prompt_template_id: str = "agent_system_v1"
    system_instruction_override: str = "You are an autonomous AI worker agent operating within the Volta platform."
    provider: str = "mock"
    model: str = "mock-model-v1"
    temperature: float = 0.7
    max_tokens: int = 2048
