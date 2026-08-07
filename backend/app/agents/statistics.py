from pydantic import BaseModel, Field


class AgentStatistics(BaseModel):
    total_registered_agents: int = Field(default=0, ge=0)
    total_tasks_executed: int = Field(default=0, ge=0)
    total_delegations: int = Field(default=0, ge=0)
    total_messages_sent: int = Field(default=0, ge=0)
    active_workers_count: int = Field(default=0, ge=0)
    average_task_latency_ms: float = Field(default=0.0, ge=0.0)
