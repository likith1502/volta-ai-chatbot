from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.integrations.capabilities import CapabilityFeatureFlags, IntegrationCapability
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.lifecycle import IntegrationLifecycleManager, IntegrationLifecycleState
from app.integrations.manifest import PluginManifest
from app.integrations.status import IntegrationStatus


class IntegrationHealthReport(BaseModel):
    """Detailed operational health report for an integration provider."""

    provider_id: str
    provider_name: str
    provider_type: str
    version: str = "1.0.0"
    is_healthy: bool = True
    health_level: HealthLevel = HealthLevel.GREEN
    status: IntegrationStatus = IntegrationStatus.CONNECTED
    latency_ms: float = Field(default=0.0, ge=0.0)
    last_success_ts: float = Field(default_factory=lambda: 1786088000.0)
    last_failure_ts: Optional[float] = None
    uptime_pct: float = Field(default=100.0, ge=0.0, le=100.0)
    availability_pct: float = Field(default=100.0, ge=0.0, le=100.0)
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    pool_active_connections: int = Field(default=1, ge=0)
    pool_max_connections: int = Field(default=10, ge=1)
    details: dict[str, Any] = Field(default_factory=dict)


class IntegrationProvider(ABC):
    """Abstract interface for all enterprise integration adapters."""

    def __init__(self, provider_id: str, name: str, category: IntegrationCapability, priority: int = 10) -> None:
        self._provider_id = provider_id
        self._name = name
        self._category = category
        self._priority = priority
        self._weight = 1.0
        self._preferred = False
        self._status = IntegrationStatus.UNKNOWN
        self._health_level = HealthLevel.GREEN
        self._lifecycle = IntegrationLifecycleManager()
        self._context = IntegrationContext()
        self._manifest = PluginManifest(
            id=provider_id,
            name=name,
            category=category,
        )

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> IntegrationCapability:
        return self._category

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def status(self) -> IntegrationStatus:
        return self._status

    @property
    def health_level(self) -> HealthLevel:
        return self._health_level

    @property
    def manifest(self) -> PluginManifest:
        return self._manifest

    @abstractmethod
    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        pass

    @abstractmethod
    async def connect(self) -> bool:
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        pass

    @abstractmethod
    async def check_health(self) -> IntegrationHealthReport:
        pass

    def pool_status(self) -> dict[str, Any]:
        return {"active_connections": 1, "max_connections": 10, "idle": 9}

    def active_connections(self) -> int:
        return 1

    def max_connections(self) -> int:
        return 10
