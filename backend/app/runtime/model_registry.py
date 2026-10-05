from typing import Optional
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """Model capabilities and cost metadata record."""

    model_id: str
    display_name: str
    provider_name: str
    supports_tools: bool = True
    supports_streaming: bool = True
    context_window_tokens: int = 128000
    input_cost_per_1k_tokens_usd: float = 0.0001
    output_cost_per_1k_tokens_usd: float = 0.0004
    status: str = "active"


class ModelRegistry:
    """Registry managing available LLM model definitions and pricing metadata across providers."""

    def __init__(self) -> None:
        self._models: dict[str, ModelInfo] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Registers default model metadata definitions for Gemini and Mock providers."""
        defaults = [
            ModelInfo(
                model_id="gemini-2.5-flash",
                display_name="Gemini 2.5 Flash",
                provider_name="gemini",
                supports_tools=True,
                supports_streaming=True,
                context_window_tokens=1048576,
                input_cost_per_1k_tokens_usd=0.000075,
                output_cost_per_1k_tokens_usd=0.0003,
                status="active",
            ),
            ModelInfo(
                model_id="gemini-2.5-pro",
                display_name="Gemini 2.5 Pro",
                provider_name="gemini",
                supports_tools=True,
                supports_streaming=True,
                context_window_tokens=2097152,
                input_cost_per_1k_tokens_usd=0.00125,
                output_cost_per_1k_tokens_usd=0.005,
                status="active",
            ),
            ModelInfo(
                model_id="mock-model-v1",
                display_name="Mock Model v1 (Deterministic)",
                provider_name="mock",
                supports_tools=True,
                supports_streaming=True,
                context_window_tokens=32768,
                input_cost_per_1k_tokens_usd=0.0,
                output_cost_per_1k_tokens_usd=0.0,
                status="active",
            ),
        ]
        for m in defaults:
            self.register(m)

    def register(self, model_info: ModelInfo) -> None:
        """Registers a ModelInfo object."""
        self._models[model_info.model_id] = model_info

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Retrieves model metadata by model_id or returns None if unlisted."""
        return self._models.get(model_id)

    def list_models(self, provider: Optional[str] = None) -> list[ModelInfo]:
        """Returns all registered models, optionally filtered by provider_name."""
        if provider:
            return [m for m in self._models.values() if m.provider_name.lower() == provider.lower()]
        return list(self._models.values())
