import asyncio
import uuid
from typing import AsyncIterator, Union

from app.runtime.base import RuntimeProvider
from app.runtime.contracts import (
    ChatMessage,
    ProviderCapabilities,
    RuntimeRequest,
    RuntimeResponse,
    RuntimeTokenUsage,
)
from app.streaming import StreamMessage


class MockProvider(RuntimeProvider):
    """Deterministic mock provider for unit testing, offline development, CI pipelines, and demonstration mode."""

    def __init__(self, latency_ms: float = 10.0) -> None:
        self._latency_ms = latency_ms
        self._initialized = False

    @property
    def name(self) -> str:
        return "mock"

    async def initialize(self) -> None:
        self._initialized = True

    async def generate(self, request: RuntimeRequest) -> RuntimeResponse:
        if not self._initialized:
            await self.initialize()

        if self._latency_ms > 0:
            await asyncio.sleep(self._latency_ms / 1000.0)

        last_user_prompt = ""
        for msg in reversed(request.messages):
            if msg.role == "user":
                last_user_prompt = msg.content
                break

        response_content = (
            f"[Mock LLM Response] Echo: '{last_user_prompt}'"
            if last_user_prompt
            else "[Mock LLM Response] Hello! I am the deterministic Volta AI Chatbot Mock Provider."
        )

        prompt_tokens = self.count_tokens(request.messages)
        completion_tokens = len(response_content) // 4
        total_tokens = prompt_tokens + completion_tokens

        return RuntimeResponse(
            response_id=uuid.uuid4(),
            content=response_content,
            role="assistant",
            provider=self.name,
            model=request.model or "mock-model-v1",
            finish_reason="stop",
            token_usage=RuntimeTokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=0.0,
            ),
            metadata={"simulated_latency_ms": self._latency_ms},
        )

    async def generate_stream(
        self, request: RuntimeRequest
    ) -> AsyncIterator[StreamMessage]:
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
            supported_models=["mock-model-v1", "mock-model-v2"],
        )

    async def health_check(self) -> bool:
        return True
