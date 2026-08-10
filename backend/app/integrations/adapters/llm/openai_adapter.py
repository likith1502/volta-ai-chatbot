import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.llm.llm_adapter import LLMAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.llm.openai")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False


class OpenAILLMAdapter(LLMAdapter):
    """Production OpenAI LLM Adapter using openai SDK with lazy loading, timeouts, and secret redaction."""

    def __init__(
        self,
        default_model: str = "gpt-4o",
        connect_timeout: float = 5.0,
        request_timeout: float = 15.0,
        max_retries: int = 3,
    ) -> None:
        super().__init__(provider_id="llm.openai", name="OpenAI GPT-4 LLM Adapter", priority=90)
        self.default_model = default_model
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self._client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without making external network calls."""
        if context:
            self._context = context

        api_key = self._context.resolved_secrets.get("OPENAI_API_KEY")
        model = self._context.resolved_secrets.get("OPENAI_MODEL", self.default_model)
        self.default_model = model

        if not OPENAI_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("OpenAILLMAdapter initialized without openai dependency.")
            return

        if not api_key:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("OpenAILLMAdapter initialized without OPENAI_API_KEY.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_client(self) -> Any:
        """Lazily instantiates OpenAI client."""
        if not OPENAI_AVAILABLE:
            raise RuntimeError("openai package is unavailable. Install 'openai' to enable OpenAI LLM provider.")

        if self._client is None:
            api_key = self._context.resolved_secrets.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY missing from context secrets.")

            def _init():
                return openai.OpenAI(
                    api_key=api_key,
                    timeout=self.request_timeout,
                    max_retries=self.max_retries,
                )

            self._client = await asyncio.to_thread(_init)

        return self._client

    async def connect(self) -> bool:
        """Verifies readiness without network calls."""
        if not OPENAI_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        api_key = self._context.resolved_secrets.get("OPENAI_API_KEY")
        if not api_key:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically closes OpenAI client session."""
        if self._client is not None:
            def _close():
                if hasattr(self._client, "close"):
                    self._client.close()

            await asyncio.to_thread(_close)
            self._client = None

        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates completion text using OpenAI ChatCompletion API."""
        client = await self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        def _generate():
            res = client.chat.completions.create(
                model=self.default_model,
                messages=messages,
            )
            return res.choices[0].message.content or ""

        return await asyncio.to_thread(_generate)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not OPENAI_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="OpenAI",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "openai package not installed"},
            )

        api_key = self._context.resolved_secrets.get("OPENAI_API_KEY")
        if not api_key:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="OpenAI",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "OPENAI_API_KEY missing from secrets"},
            )

        try:
            client = await self._get_client()

            def _check():
                client.models.list()

            await asyncio.to_thread(_check)
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="OpenAI",
                is_healthy=True,
                health_level=HealthLevel.GREEN,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"model": self.default_model},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="OpenAI",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
