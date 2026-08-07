"""Deployment events — typed event bus for lifecycle notifications."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DeploymentEvent:
    event_type: str
    deployment_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 1786088000.0


class DeploymentEventBus:
    def __init__(self) -> None:
        self._events: list[DeploymentEvent] = []

    def emit(self, event: DeploymentEvent) -> None:
        self._events.append(event)

    def get_events(self, deployment_id: str | None = None) -> list[DeploymentEvent]:
        if deployment_id:
            return [e for e in self._events if e.deployment_id == deployment_id]
        return list(self._events)
