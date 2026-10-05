import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.llm.llm_adapter import LLMAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.llm.anthropic")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    anthropic = None
    ANTHROPIC_AVAILABLE = False


class AnthropicLLMAdapter(LLMAdapter):
    """Production Anthropic Claude LLM Adapter using anthropic SDK with lazy loading, timeouts, and secret redaction."""

    def __init__(
        self,
        default_model: str = "claude-3-5-sonnet-20241022",
        connect_timeout: float = 5.0,
        request_timeout: float = 15.0,
        max_retries: int = 3,
    ) -> None:
        super().__init__(provider_id="llm.anthropic", name="Anthropic Claude LLM Adapter", priority=85)
        self.default_model = default_model
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self._client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without making network calls."""
        if context:
            self._context = context

        api_key = self._context.resolved_secrets.get("ANTHROPIC_API_KEY")
        model = self._context.resolved_secrets.get("ANTHROPIC_MODEL", self.default_model)
        self.default_model = model

        if not ANTHROPIC_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("AnthropicLLMAdapter initialized without anthropic dependency.")
            return

        if not api_key:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("AnthropicLLMAdapter initialized without ANTHROPIC_API_KEY.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_client(self) -> Any:
        """Lazily instantiates Anthropic client."""
        if not ANTHROPIC_AVAILABLE:
            raise RuntimeError("anthropic package is unavailable. Install 'anthropic' to enable Anthropic LLM provider.")

        if self._client is None:
            api_key = self._context.resolved_secrets.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY missing from context secrets.")

            def _init():
                return anthropic.Anthropic(
                    api_key=api_key,
                    timeout=self.request_timeout,
                    max_retries=self.max_retries,
                )

            self._client = await asyncio.to_thread(_init)

        return self._client

    async def connect(self) -> bool:
        """Verifies readiness without network calls."""
        if not ANTHROPIC_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        api_key = self._context.resolved_secrets.get("ANTHROPIC_API_KEY")
        if not api_key:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically closes Anthropic client session."""
        if self._client is not None:
            def _close():
                if hasattr(self._client, "close"):
                    self._client.close()

            await asyncio.to_thread(_close)
            self._client = None

        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates text completion using Anthropic Messages API."""
        client = await self._get_client()

        kwargs: dict[str, Any] = {
            "model": self.default_model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        def _generate():
            res = client.messages.create(**kwargs)
            if res.content and len(res.content) > 0:
                return getattr(res.content[0], "text", "")
            return ""

        return await asyncio.to_thread(_generate)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not ANTHROPIC_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Anthropic",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "anthropic package not installed"},
            )

        api_key = self._context.resolved_secrets.get("ANTHROPIC_API_KEY")
        if not api_key:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Anthropic",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "ANTHROPIC_API_KEY missing from secrets"},
            )

        try:
            client = await self._get_client()
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Anthropic",
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
                provider_type="Anthropic",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
