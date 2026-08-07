from typing import Optional
from pydantic import BaseModel, Field
from app.config.settings import settings


class ProviderConfig(BaseModel):
    """Specific configuration container for individual LLM providers."""

    provider_name: str
    api_key: Optional[str] = None
    endpoint_url: Optional[str] = None
    timeout: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=3, ge=0)


class GenerationConfig(BaseModel):
    """Generation controls for LLM completion requests."""

    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=1)
    max_tokens: int = Field(default=1000, ge=1)


class RuntimeConfig(BaseModel):
    """Enterprise LLM Runtime Engine composite configuration container."""

    default_provider: str = Field(default_factory=lambda: settings.RUNTIME_DEFAULT_PROVIDER)
    default_model: str = Field(default_factory=lambda: settings.RUNTIME_DEFAULT_MODEL)
    timeout: float = Field(default_factory=lambda: settings.RUNTIME_TIMEOUT)
    max_retries: int = Field(default_factory=lambda: settings.RUNTIME_MAX_RETRIES)
    demo_mode: bool = Field(default_factory=lambda: settings.DEMO_MODE)
    generation_defaults: GenerationConfig = Field(default_factory=GenerationConfig)
