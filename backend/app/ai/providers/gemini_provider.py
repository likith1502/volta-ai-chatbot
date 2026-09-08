import logging
from typing import Any, Optional

import httpx

from app.ai.base import AIProvider
from app.ai.exceptions import (
    AIProviderException,
    ModelUnavailableException,
    PromptTooLargeException,
    RateLimitException,
)
from app.ai.models import AIRequest, AIResponse, AITokenUsage
from app.config.settings import settings

logger = logging.getLogger("app.ai.providers.gemini")


class GeminiProvider(AIProvider):
    """Google Gemini Chat Completions API Provider implementation (OpenAI-compatible endpoint)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self.api_key = (
            api_key if api_key is not None else settings.GEMINI_API_KEY
        )
        self.model = model or settings.GEMINI_MODEL
        self.temperature = (
            temperature if temperature is not None else settings.GEMINI_TEMPERATURE
        )
        self.max_tokens = max_tokens or settings.GEMINI_MAX_TOKENS
        self.timeout = timeout or settings.GEMINI_TIMEOUT

    async def generate_response(self, request: AIRequest) -> AIResponse:
        """Invokes Google Gemini Chat Completions REST API and maps response to AIResponse."""
        messages_payload = []
        if request.system_prompt:
            messages_payload.append(
                {"role": "system", "content": request.system_prompt}
            )

        for msg in request.messages:
            messages_payload.append({"role": msg.role, "content": msg.content})

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages_payload,
        }

        # Google has deprecated sampling parameters (temperature, top_p, top_k) for Gemini 3.x models
        is_gemini_3 = "gemini-3" in self.model.lower()
        if not is_gemini_3:
            temp = (
                request.temperature
                if request.temperature is not None
                else self.temperature
            )
            if temp is not None:
                payload["temperature"] = temp

        max_tok = (
            request.max_tokens
            if request.max_tokens is not None
            else self.max_tokens
        )
        if max_tok is not None:
            payload["max_tokens"] = max_tok

        # If API key is missing (e.g. mock/fallback mode), simulate/return structured response
        if not self.api_key or self.api_key == "mock":
            logger.info(
                "Gemini API key unconfigured or mock mode active. Generating fallback completion."
            )
            last_msg = request.messages[-1].content if request.messages else "Hello"
            return AIResponse(
                content=f"Hello! I am your Volta AI mobility assistant (Gemini). I received your message: '{last_msg}'. How can I help you book a ride or plan your route today?",
                role="assistant",
                model_used=self.model,
                finish_reason="stop",
                usage=AITokenUsage(
                    prompt_tokens=15, completion_tokens=25, total_tokens=40
                ),
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                    headers=headers,
                    json=payload,
                )

                if response.status_code == 429:
                    raise RateLimitException("Gemini API rate limit or quota exceeded.")
                elif response.status_code == 400:
                    raise PromptTooLargeException(
                        f"Gemini bad request: {response.text}"
                    )
                elif response.status_code in (500, 502, 503, 504):
                    raise ModelUnavailableException(
                        "Gemini service temporarily unavailable."
                    )
                elif response.status_code != 200:
                    raise AIProviderException(
                        message=f"Gemini error status {response.status_code}: {response.text}",
                        status_code=response.status_code,
                    )

                data = response.json()
                choice = data["choices"][0]
                usage_data = data.get("usage", {})

                return AIResponse(
                    content=choice["message"]["content"],
                    role=choice["message"].get("role", "assistant"),
                    model_used=data.get("model", self.model),
                    finish_reason=choice.get("finish_reason", "stop"),
                    usage=AITokenUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                        total_tokens=usage_data.get("total_tokens", 0),
                    ),
                )
        except httpx.TimeoutException:
            raise ModelUnavailableException("Timeout waiting for Gemini response.")
        except httpx.RequestError as exc:
            raise ModelUnavailableException(
                f"Network error connecting to Gemini: {exc}"
            )
