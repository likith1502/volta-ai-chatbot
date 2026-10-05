import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.llm.llm_adapter import LLMAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.llm.ollama")

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    httpx = None
    HTTPX_AVAILABLE = False


class OllamaLLMAdapter(LLMAdapter):
    """Production Ollama Local LLM Adapter using httpx REST API with lazy loading and timeouts."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "llama3",
        connect_timeout: float = 5.0,
        request_timeout: float = 30.0,
    ) -> None:
        super().__init__(provider_id="llm.ollama", name="Ollama Local LLM Adapter", priority=50)
        self.base_url = base_url
        self.default_model = default_model
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape without making external network calls."""
        if context:
            self._context = context

        url = self._context.resolved_secrets.get("OLLAMA_HOST", self.base_url)
        model = self._context.resolved_secrets.get("OLLAMA_MODEL", self.default_model)
        self.base_url = url
        self.default_model = model

        if not HTTPX_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("OllamaLLMAdapter initialized without httpx dependency.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_client(self) -> Any:
        """Lazily instantiates AsyncClient for HTTP calls to Ollama server."""
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx package is unavailable. Install 'httpx' to enable Ollama LLM provider.")

        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.request_timeout, connect=self.connect_timeout),
            )

        return self._client

    async def connect(self) -> bool:
        """Verifies readiness."""
        if not HTTPX_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically closes httpx client session."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def generate_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generates text completion calling local Ollama /api/generate endpoint."""
        client = await self._get_client()

        payload: dict[str, Any] = {
            "model": self.default_model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        res = await client.post("/api/generate", json=payload)
        res.raise_for_status()
        data = res.json()
        return data.get("response", "")

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check calling /api/tags."""
        start_time = time.perf_counter()

        if not HTTPX_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Ollama",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "httpx package not installed"},
            )

        try:
            client = await self._get_client()
            res = await client.get("/api/tags")
            latency = (time.perf_counter() - start_time) * 1000.0
            if res.status_code == 200:
                return IntegrationHealthReport(
                    provider_id=self.provider_id,
                    provider_name=self.name,
                    provider_type="Ollama",
                    is_healthy=True,
                    health_level=HealthLevel.GREEN,
                    status=IntegrationStatus.CONNECTED,
                    latency_ms=round(latency, 2),
                    details={"model": self.default_model, "base_url": self.base_url},
                )
            else:
                return IntegrationHealthReport(
                    provider_id=self.provider_id,
                    provider_name=self.name,
                    provider_type="Ollama",
                    is_healthy=False,
                    health_level=HealthLevel.RED,
                    status=IntegrationStatus.DEGRADED,
                    latency_ms=round(latency, 2),
                    details={"error": "connection_failure", "status_code": res.status_code},
                )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="Ollama",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
