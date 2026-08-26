import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Structured, extensible chat message primitive supporting multi-role conversational turns."""

    role: str = Field(
        default="user",
        description="Message role: 'system', 'user', 'assistant', 'tool'",
    )
    content: str = Field(..., description="Text content payload")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata envelope for multimodal attachments or tool IDs",
    )


class RuntimeTokenUsage(BaseModel):
    """Standardized token accounting metrics and estimated cost calculation."""

    prompt_tokens: int = Field(default=0, ge=0)
    completion_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0.0, ge=0.0)


class ProviderCapabilities(BaseModel):
    """Capability reporting flags for AI providers."""

    provider_name: str
    supports_streaming: bool = True
    supports_tools: bool = True
    supports_system_prompts: bool = True
    supported_models: list[str] = Field(default_factory=list)


class RuntimeRequest(BaseModel):
    """Immutable runtime execution request container."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    conversation_id: Optional[uuid.UUID] = None
    execution_id: Optional[uuid.UUID] = None
    messages: list[ChatMessage] = Field(..., min_length=1)
    system_prompt: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RuntimeResponse(BaseModel):
    """Standardized provider-independent LLM generation payload."""

    response_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    content: str
    role: str = "assistant"
    provider: str
    model: str
    finish_reason: Optional[str] = "stop"
    token_usage: RuntimeTokenUsage = Field(default_factory=RuntimeTokenUsage)
    metadata: dict[str, Any] = Field(default_factory=dict)
