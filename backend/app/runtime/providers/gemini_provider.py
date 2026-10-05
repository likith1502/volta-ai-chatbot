import asyncio
import logging
import os
import uuid
from typing import AsyncIterator, Union

from app.config.settings import settings
from app.runtime.base import RuntimeProvider
from app.runtime.contracts import ChatMessage, ProviderCapabilities, RuntimeRequest, RuntimeResponse, RuntimeTokenUsage
from app.runtime.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderInitializationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
    RuntimeExecutionError,
)
from app.streaming import StreamMessage

logger = logging.getLogger("app.runtime.providers.gemini")


class GeminiProvider(RuntimeProvider):
    """Production LLM runtime provider integrating the official Google GenAI SDK (`google.genai`)."""

    def __init__(self, api_key: str = "", default_model: str = "gemini-2.5-flash") -> None:
        self._api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        self._default_model = default_model or settings.GEMINI_MODEL
        self._client = None
        self._initialized = False

    @property
    def name(self) -> str:
        return "gemini"

    async def initialize(self) -> None:
        """Initializes Google GenAI client instance."""
        if self._initialized:
            return

        try:
            import google.genai as genai  # type: ignore

            if self._api_key and self._api_key.strip():
                self._client = genai.Client(api_key=self._api_key.strip())
            else:
                # Attempt default initialization if client environment is set
                self._client = genai.Client()

            self._initialized = True
            logger.info("GeminiProvider initialized successfully with google.genai SDK")
        except Exception as exc:
            self._initialized = False
            logger.warning(f"GeminiProvider initialization notice: {exc}")

    async def generate(self, request: RuntimeRequest) -> RuntimeResponse:
        """Executes generation turn using google.genai SDK."""
        if not self._initialized:
            await self.initialize()

        if not self._api_key or not self._api_key.strip():
            raise ProviderConfigurationError("Gemini API key is not configured in GEMINI_API_KEY or GOOGLE_API_KEY environment variables.")

        if not self._client:
            raise ProviderInitializationError("Google GenAI client is not initialized.")

        model_name = request.model or self._default_model
        
        # Build contents from ChatMessages
        contents = []
        if request.system_prompt:
            contents.append(f"System: {request.system_prompt}")

        for msg in request.messages:
            if msg.role == "system":
                contents.append(f"System: {msg.content}")
            elif msg.role == "user":
                contents.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                contents.append(f"Model: {msg.content}")

        try:
            # Execute async generation via SDK client
            loop = asyncio.get_running_loop()
            
            def _call_genai():
                return self._client.models.generate_content(
                    model=model_name,
                    contents=contents,
                )

            res = await loop.run_in_executor(None, _call_genai)
            
            response_text = res.text if hasattr(res, "text") and res.text else str(res)
            
            # Extract usage metrics if returned by SDK
            prompt_tokens = 0
            completion_tokens = 0
            if hasattr(res, "usage_metadata") and res.usage_metadata:
                prompt_tokens = getattr(res.usage_metadata, "prompt_token_count", 0) or 0
                completion_tokens = getattr(res.usage_metadata, "candidates_token_count", 0) or 0
            
            if prompt_tokens == 0:
                prompt_tokens = self.count_tokens(request.messages)
            if completion_tokens == 0:
                completion_tokens = max(1, len(response_text) // 4)

            total_tokens = prompt_tokens + completion_tokens

            # Calculate estimated USD cost
            cost_per_1k_input = 0.000075 if "flash" in model_name else 0.00125
            cost_per_1k_output = 0.0003 if "flash" in model_name else 0.005
            estimated_cost = ((prompt_tokens / 1000.0) * cost_per_1k_input) + ((completion_tokens / 1000.0) * cost_per_1k_output)

            return RuntimeResponse(
                response_id=uuid.uuid4(),
                content=response_text,
                role="assistant",
                provider=self.name,
                model=model_name,
                finish_reason="stop",
                token_usage=RuntimeTokenUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    estimated_cost_usd=estimated_cost,
                ),
                metadata={"sdk": "google-genai"},
            )
        except Exception as exc:
            err_msg = str(exc).lower()
            if "api_key" in err_msg or "auth" in err_msg or "unauthorized" in err_msg:
                raise ProviderAuthenticationError(f"Gemini API authentication failed: {exc}")
            elif "429" in err_msg or "quota" in err_msg or "rate" in err_msg:
                raise ProviderRateLimitError(f"Gemini API rate limit exceeded: {exc}")
            elif "503" in err_msg or "unavailable" in err_msg:
                raise ProviderUnavailableError(f"Gemini API service unavailable: {exc}")
            raise RuntimeExecutionError(f"Gemini API execution failed: {exc}")

    async def generate_stream(self, request: RuntimeRequest) -> AsyncIterator[StreamMessage]:
        """Streaming response implementation yielding StreamMessage tokens."""
        if not self._initialized:
            await self.initialize()

        res = await self.generate(request)
        words = res.content.split(" ")
        for idx, word in enumerate(words):
            token_text = word + (" " if idx < len(words) - 1 else "")
            yield StreamMessage(
                stream_id=uuid.uuid4(),
                event_type="token",
                payload={"token": token_text, "sequence": idx},
                sequence_number=idx + 1,
            )
            await asyncio.sleep(0.01)

    def count_tokens(self, content: Union[str, list[ChatMessage]]) -> int:
        """Estimates token count for given text or list of ChatMessages."""
        if isinstance(content, str):
            return max(1, len(content) // 4)
        total_chars = sum(len(m.content) for m in content)
        return max(1, total_chars // 4)

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            provider_name=self.name,
            supports_streaming=True,
            supports_tools=True,
            supports_system_prompts=True,
            supported_models=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash", "gemini-1.5-pro"],
        )

    async def health_check(self) -> bool:
        """Checks if Gemini provider SDK is installed and API key is present."""
        if not self._initialized:
            try:
                await self.initialize()
            except Exception:
                return False
        return bool(self._api_key and self._api_key.strip())
