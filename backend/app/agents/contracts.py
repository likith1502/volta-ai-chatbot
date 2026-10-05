import uuid
from typing import Any, Optional
from pydantic import BaseModel, Field


class AgentRegisterPayload(BaseModel):
    name: str = Field(..., min_length=1)
    role: str = "support"
    communication_style: str = "professional"
    tone: str = "helpful"


class AgentExecutePayload(BaseModel):
    agent_id: str
    task_title: str = Field(..., min_length=1)
    inputs: dict[str, Any] = Field(default_factory=dict)


class AgentDelegatePayload(BaseModel):
    delegator_agent_id: str
    delegatee_agent_id: str
    task_title: str = Field(..., min_length=1)
    inputs: dict[str, Any] = Field(default_factory=dict)
    current_depth: int = 1


class AgentMessagePayload(BaseModel):
    sender_agent_id: str
    recipient_agent_id: str
    content: str = Field(..., min_length=1)


class AgentTaskPayload(BaseModel):
    title: str = Field(..., min_length=1)
    priority: int = Field(default=1, ge=1, le=10)
    inputs: dict[str, Any] = Field(default_factory=dict)


class TeamCreatePayload(BaseModel):
    name: str = Field(..., min_length=1)
    supervisor_id: str
    member_ids: list[str] = Field(default_factory=list)


class AgentResponse(BaseModel):
    success: bool = True
    data: dict[str, Any]
    message: str = "Operation completed"
