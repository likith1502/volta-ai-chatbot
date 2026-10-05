from pydantic import BaseModel, Field
from app.memory.memory import Memory


class MemoryChainStep(BaseModel):
    """Step representation in a multi-memory chain."""

    step_id: str
    target_memory_type: str
    action: str = Field(default="retrieve", description="'retrieve', 'store', 'update'")


class MemoryChain(BaseModel):
    """Multi-memory operation chain container."""

    chain_id: str
    steps: list[MemoryChainStep] = Field(default_factory=list)
