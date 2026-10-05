"""Scaling Engine — AutoScalingPolicy, HorizontalScaling, VerticalScaling, ResourceLimits, ReplicaPolicy."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ScalingDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    NONE = "none"


@dataclass
class ResourceLimits:
    """CPU and memory resource limits for a deployment."""
    cpu_request: str = "250m"
    cpu_limit: str = "1000m"
    memory_request: str = "512Mi"
    memory_limit: str = "2Gi"
    gpu_count: int = 0


@dataclass
class ReplicaPolicy:
    """Replica count policy for a deployment target."""
    min_replicas: int = 1
    max_replicas: int = 10
    desired_replicas: int = 2
    scale_up_cooldown_seconds: int = 60
    scale_down_cooldown_seconds: int = 300


@dataclass
class AutoScalingPolicy:
    """Policy controlling auto-scaling trigger thresholds."""
    enabled: bool = True
    cpu_threshold_pct: float = 70.0
    memory_threshold_pct: float = 80.0
    request_rate_threshold: int = 500
    latency_p95_ms_threshold: float = 200.0
    custom_metrics: dict[str, float] = field(default_factory=dict)


@dataclass
class ScalingEvent:
    """A recorded scaling event."""
    event_id: str
    deployment_id: str
    direction: ScalingDirection
    from_replicas: int
    to_replicas: int
    trigger: str
    timestamp: float = 1786088000.0
    metadata: dict[str, Any] = field(default_factory=dict)


class HorizontalScaling:
    """Horizontal Pod Autoscaler — adds/removes replica instances."""

    def __init__(self, policy: ReplicaPolicy, auto_policy: AutoScalingPolicy) -> None:
        self.policy = policy
        self.auto_policy = auto_policy
        self._events: list[ScalingEvent] = []

    def compute_desired_replicas(self, current_replicas: int, cpu_pct: float, memory_pct: float) -> int:
        """Compute target replica count based on resource utilisation."""
        if cpu_pct >= self.auto_policy.cpu_threshold_pct or memory_pct >= self.auto_policy.memory_threshold_pct:
            return min(current_replicas + 1, self.policy.max_replicas)
        if cpu_pct < self.auto_policy.cpu_threshold_pct * 0.4 and current_replicas > self.policy.min_replicas:
            return max(current_replicas - 1, self.policy.min_replicas)
        return current_replicas

    async def scale(self, deployment_id: str, current: int, target: int) -> ScalingEvent:
        direction = (
            ScalingDirection.UP if target > current
            else ScalingDirection.DOWN if target < current
            else ScalingDirection.NONE
        )
        evt = ScalingEvent(
            event_id=f"hpa_{deployment_id}_{len(self._events)}",
            deployment_id=deployment_id,
            direction=direction,
            from_replicas=current,
            to_replicas=target,
            trigger="hpa",
        )
        self._events.append(evt)
        return evt

    @property
    def events(self) -> list[ScalingEvent]:
        return list(self._events)


class VerticalScaling:
    """Vertical Pod Autoscaler — adjusts resource limits per pod."""

    def __init__(self, limits: ResourceLimits) -> None:
        self.current_limits = limits
        self._history: list[ResourceLimits] = [limits]

    def recommend(self, cpu_pct: float, memory_pct: float) -> ResourceLimits:
        """Produce a resource recommendation based on observed utilisation."""
        new_cpu = "500m" if cpu_pct > 75 else self.current_limits.cpu_request
        new_mem = "1Gi" if memory_pct > 80 else self.current_limits.memory_request
        return ResourceLimits(
            cpu_request=new_cpu,
            cpu_limit=self.current_limits.cpu_limit,
            memory_request=new_mem,
            memory_limit=self.current_limits.memory_limit,
        )

    def apply(self, new_limits: ResourceLimits) -> None:
        self._history.append(self.current_limits)
        self.current_limits = new_limits

    @property
    def history(self) -> list[ResourceLimits]:
        return list(self._history)
