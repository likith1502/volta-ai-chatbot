from pydantic import BaseModel, Field
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.registry import IntegrationRegistry


class AggregatedPlatformHealth(BaseModel):
    """Aggregated health report across all 10 integration categories."""

    overall_health: HealthLevel = HealthLevel.GREEN
    overall_status: str = "Enterprise Integration Platform operational"
    active_providers_count: int = Field(default=0, ge=0)
    category_health: dict[str, HealthLevel] = Field(default_factory=dict)
    provider_reports: list[IntegrationHealthReport] = Field(default_factory=list)


class IntegrationHealthManager:
    """Central platform health aggregator inspecting all registered adapters."""

    def __init__(self, registry: IntegrationRegistry) -> None:
        self.registry = registry

    async def check_platform_health(self) -> AggregatedPlatformHealth:
        providers = self.registry.list_providers()
        reports: list[IntegrationHealthReport] = []
        cat_health: dict[str, HealthLevel] = {}

        has_yellow = False
        has_orange = False
        has_red = False

        for p in providers:
            rep = await p.check_health()
            reports.append(rep)
            cat_health[p.category.value] = rep.health_level

            if rep.health_level == HealthLevel.YELLOW:
                has_yellow = True
            elif rep.health_level == HealthLevel.ORANGE:
                has_orange = True
            elif rep.health_level == HealthLevel.RED:
                has_red = True

        overall = HealthLevel.GREEN
        if has_red:
            overall = HealthLevel.RED
        elif has_orange:
            overall = HealthLevel.ORANGE
        elif has_yellow:
            overall = HealthLevel.YELLOW

        return AggregatedPlatformHealth(
            overall_health=overall,
            overall_status=f"Platform Health: {overall.value.upper()}",
            active_providers_count=len(providers),
            category_health=cat_health,
            provider_reports=reports,
        )
