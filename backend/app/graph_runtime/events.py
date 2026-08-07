from pydantic import BaseModel, Field


class GraphExecutionStartedEvent(BaseModel):
    execution_id: str
    workflow_id: str


class GraphNodeStartedEvent(BaseModel):
    execution_id: str
    node_id: str


class GraphNodeCompletedEvent(BaseModel):
    execution_id: str
    node_id: str
    latency_ms: float


class GraphExecutionCompletedEvent(BaseModel):
    execution_id: str
    workflow_id: str
    duration_ms: float


class GraphExecutionInterruptedEvent(BaseModel):
    execution_id: str
    node_id: str
    reason: str
