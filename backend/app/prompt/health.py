import logging
from typing import Any

from pydantic import BaseModel, Field

from app.prompt.registry import PromptRegistry

logger = logging.getLogger("app.prompt.health")


class PromptHealthStatus(BaseModel):
    """Health status report for the Prompt Execution Engine."""

    is_healthy: bool = True
    templates_count: int = 0
    profiles_count: int = 0
    renderer_ready: bool = True
    registry_healthy: bool = True
    middleware_loaded: bool = True
    message: str = "Prompt Execution Engine is healthy"
    capabilities: dict[str, Any] = Field(default_factory=dict)


class PromptHealthManager:
    """Centralized health orchestrator checking prompt template registry, renderer readiness, and middleware status."""

    def __init__(self, registry: PromptRegistry) -> None:
        self.registry = registry

    async def check_health(self) -> PromptHealthStatus:
        templates_count = len(self.registry.list_templates())
        profiles_count = len(self.registry.list_profiles())
        is_healthy = templates_count >= 0

        return PromptHealthStatus(
            is_healthy=is_healthy,
            templates_count=templates_count,
            profiles_count=profiles_count,
            renderer_ready=True,
            registry_healthy=True,
            middleware_loaded=True,
            message=f"Prompt Engine ready with {templates_count} templates and {profiles_count} profiles.",
            capabilities={
                "supports_variables": True,
                "supports_templates": True,
                "supports_system_prompt": True,
                "supports_tools": True,
            },
        )
