from pydantic import BaseModel


class AgentRegisteredEvent(BaseModel):
    agent_id: str
    name: str
    role: str


class AgentStartedEvent(BaseModel):
    agent_id: str
    task_id: str


class AgentDelegatedEvent(BaseModel):
    delegator_id: str
    delegatee_id: str
    task_id: str
    depth: int


class AgentTaskCompletedEvent(BaseModel):
    agent_id: str
    task_id: str
    latency_ms: float
