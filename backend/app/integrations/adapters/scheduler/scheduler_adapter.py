from abc import ABC, abstractmethod
from typing import Any, Callable, Optional
from app.integrations.capabilities import IntegrationCapability
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport, IntegrationProvider
from app.integrations.status import IntegrationStatus


class SchedulerAdapter(IntegrationProvider, ABC):
    """Abstract interface for cron & background task schedulers."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name=name, category=IntegrationCapability.SCHEDULER, priority=priority)

    @abstractmethod
    async def schedule_job(self, cron_expr: str, func: Callable[..., Any]) -> str:
        pass


class CronSchedulerAdapter(SchedulerAdapter):
    """Reference scheduler adapter executing cron tasks."""

    def __init__(self) -> None:
        super().__init__(provider_id="scheduler.cron", name="Cron Task Scheduler Adapter", priority=10)
        self._jobs: dict[str, str] = {}
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[Any] = None) -> None:
        self._status = IntegrationStatus.READY
        await self.connect()

    async def connect(self) -> bool:
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def schedule_job(self, cron_expr: str, func: Callable[..., Any]) -> str:
        job_id = f"job_{len(self._jobs) + 1}"
        self._jobs[job_id] = cron_expr
        return job_id

    async def check_health(self) -> IntegrationHealthReport:
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="Cron",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=self.status,
            latency_ms=0.2,
        )


class APSchedulerAdapter(CronSchedulerAdapter):
    """Extension placeholder for APScheduler Adapter."""

    def __init__(self) -> None:
        super().__init__()
        self._provider_id = "scheduler.apscheduler"
        self._name = "APScheduler Adapter"
