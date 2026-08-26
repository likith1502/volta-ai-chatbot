from pydantic import BaseModel


class ToolRegisteredEvent(BaseModel):
    tool_name: str
    version: str


class ToolValidatedEvent(BaseModel):
    tool_name: str
    is_valid: bool


class ToolStartedEvent(BaseModel):
    tool_name: str
    execution_id: str


class ToolCompletedEvent(BaseModel):
    tool_name: str
    execution_id: str
    duration_ms: float


class ToolFailedEvent(BaseModel):
    tool_name: str
    execution_id: str
    error: str


class ToolTimedOutEvent(BaseModel):
    tool_name: str
    execution_id: str
    timeout_seconds: float


class ToolSkippedEvent(BaseModel):
    tool_name: str
    reason: str


class ToolCancelledEvent(BaseModel):
    tool_name: str
    reason: str
