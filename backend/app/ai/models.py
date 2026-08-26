from typing import Any, Optional

from pydantic import BaseModel, Field


class AIMessage(BaseModel):
    """Provider-agnostic conversational message payload."""

    role: str = "user"  # "system", "user", "assistant", "tool"
    content: str


class AITokenUsage(BaseModel):
    """Standardized AI token usage metrics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class AIToolCall(BaseModel):
    """Standardized tool execution request from AI Provider."""

    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    tool_call_id: Optional[str] = None


class AIToolResult(BaseModel):
    """Standardized result returned after executing an AITool."""

    tool_name: str
    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None


class AIRequest(BaseModel):
    """Standardized AI generation request payload."""

    messages: list[AIMessage]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    system_prompt: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AIResponse(BaseModel):
    """Standardized provider-independent AI response payload."""

    content: str
    role: str = "assistant"
    model_used: str
    finish_reason: Optional[str] = None
    usage: AITokenUsage = Field(default_factory=AITokenUsage)
    tool_calls: list[AIToolCall] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
