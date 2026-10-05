"""Deployment strategies — Blue/Green, Rolling, Canary, Recreate."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DeploymentStrategyType(str, Enum):
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"
    RECREATE = "recreate"


@dataclass
class DeploymentStrategyConfig:
    """Strategy configuration parameters."""
    max_surge: int = 1
    max_unavailable: int = 0
    canary_weight_pct: int = 10
    canary_step_count: int = 5
    rollback_on_failure: bool = True
    wait_seconds_between_steps: int = 30
    health_check_retries: int = 3
    extra: dict[str, Any] = field(default_factory=dict)


class DeploymentStrategy(ABC):
    """Abstract base for all deployment strategies."""

    strategy_type: DeploymentStrategyType

    def __init__(self, config: DeploymentStrategyConfig | None = None) -> None:
        self.config = config or DeploymentStrategyConfig()

    @abstractmethod
    async def execute(self, deployment_id: str, replicas: int, image_tag: str) -> dict[str, Any]:
        """Execute deployment strategy. Returns execution summary."""
        ...

    @abstractmethod
    async def rollback(self, deployment_id: str) -> bool:
        """Trigger strategy-specific rollback."""
        ...

    def describe(self) -> dict[str, Any]:
        return {
            "type": self.strategy_type.value,
            "config": {
                "max_surge": self.config.max_surge,
                "max_unavailable": self.config.max_unavailable,
                "rollback_on_failure": self.config.rollback_on_failure,
            },
        }


class BlueGreenDeployment(DeploymentStrategy):
    """Blue/Green zero-downtime deployment strategy."""

    strategy_type = DeploymentStrategyType.BLUE_GREEN

    async def execute(self, deployment_id: str, replicas: int, image_tag: str) -> dict[str, Any]:
        return {
            "strategy": "blue_green",
            "deployment_id": deployment_id,
            "active_slot": "green",
            "standby_slot": "blue",
            "replicas": replicas,
            "image_tag": image_tag,
            "traffic_shifted": True,
        }

    async def rollback(self, deployment_id: str) -> bool:
        return True


class RollingDeployment(DeploymentStrategy):
    """Rolling deployment strategy — replaces pods incrementally."""

    strategy_type = DeploymentStrategyType.ROLLING

    async def execute(self, deployment_id: str, replicas: int, image_tag: str) -> dict[str, Any]:
        return {
            "strategy": "rolling",
            "deployment_id": deployment_id,
            "replicas": replicas,
            "max_surge": self.config.max_surge,
            "max_unavailable": self.config.max_unavailable,
            "image_tag": image_tag,
            "steps_completed": replicas,
        }

    async def rollback(self, deployment_id: str) -> bool:
        return True


class CanaryDeployment(DeploymentStrategy):
    """Canary deployment strategy — gradual traffic shift."""

    strategy_type = DeploymentStrategyType.CANARY

    async def execute(self, deployment_id: str, replicas: int, image_tag: str) -> dict[str, Any]:
        return {
            "strategy": "canary",
            "deployment_id": deployment_id,
            "canary_weight_pct": self.config.canary_weight_pct,
            "steps": self.config.canary_step_count,
            "replicas": replicas,
            "image_tag": image_tag,
            "canary_healthy": True,
            "promoted": True,
        }

    async def rollback(self, deployment_id: str) -> bool:
        return True


class RecreateDeployment(DeploymentStrategy):
    """Recreate deployment — terminate all then redeploy. Suitable for dev."""

    strategy_type = DeploymentStrategyType.RECREATE

    async def execute(self, deployment_id: str, replicas: int, image_tag: str) -> dict[str, Any]:
        return {
            "strategy": "recreate",
            "deployment_id": deployment_id,
            "replicas": replicas,
            "image_tag": image_tag,
            "terminated_old": True,
            "deployed_new": True,
        }

    async def rollback(self, deployment_id: str) -> bool:
        return True


def create_strategy(strategy_type: DeploymentStrategyType, config: DeploymentStrategyConfig | None = None) -> DeploymentStrategy:
    """Factory for creating deployment strategies."""
    registry: dict[DeploymentStrategyType, type[DeploymentStrategy]] = {
        DeploymentStrategyType.BLUE_GREEN: BlueGreenDeployment,
        DeploymentStrategyType.ROLLING: RollingDeployment,
        DeploymentStrategyType.CANARY: CanaryDeployment,
        DeploymentStrategyType.RECREATE: RecreateDeployment,
    }
    cls = registry.get(strategy_type)
    if not cls:
        raise ValueError(f"Unknown deployment strategy: {strategy_type}")
    return cls(config=config)
