from typing import Optional
from pydantic import BaseModel, Field


class PromptProfile(BaseModel):
    """Reusable generation profile separating 'how to generate' (settings) from 'what to say' (templates)."""

    profile_id: str
    display_name: str
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=1)
    max_tokens: int = Field(default=1000, ge=1)
    response_format: str = Field(default="text", description="'text', 'json', 'markdown'")
    stop_sequences: list[str] = Field(default_factory=list)
    description: Optional[str] = None
