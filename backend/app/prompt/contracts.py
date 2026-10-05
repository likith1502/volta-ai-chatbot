import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.runtime.contracts import ChatMessage


class PromptVariable(BaseModel):
    """Structured variable definition used for template interpolation."""

    name: str
    value: Any = None
    required: bool = True
    default_value: Any = None
    description: Optional[str] = None


class PromptMessage(BaseModel):
    """Template message primitive representing a turn before rendering."""

    role: str = Field(default="user", description="'system', 'user', 'assistant', 'tool'")
    content_template: str = Field(..., description="Raw text template string containing {variable_name} placeholders")
    variables: list[PromptVariable] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptRequest(BaseModel):
    """Execution request payload for prompt rendering and optional LLM execution."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    template_id: str
    revision_id: Optional[str] = None
    profile_id: Optional[str] = None
    variables: dict[str, Any] = Field(default_factory=dict)
    system_prompt_override: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    conversation_id: Optional[uuid.UUID] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptResponse(BaseModel):
    """Rendered, provider-independent prompt payload ready for execution."""

    response_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    template_id: str
    revision_id: str = "v1"
    messages: list[ChatMessage] = Field(..., min_length=1)
    system_prompt: Optional[str] = None
    variables_applied: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CompiledPrompt(BaseModel):
    """Format-compiled prompt payload structured specifically for RuntimeManager consumption."""

    compiled_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    messages: list[ChatMessage]
    system_prompt: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
