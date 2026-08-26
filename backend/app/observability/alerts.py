"""Alert provider — email reference, Slack/PagerDuty placeholders."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class Alert:
    alert_id: str
    title: str
    severity: AlertSeverity
    message: str
    service: str = "volta-platform"
    labels: dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    fired_at: float = 1786088000.0
    resolved_at: float | None = None


class AlertProvider(ABC):
    @abstractmethod
    async def fire(self, alert: Alert) -> bool: ...

    @abstractmethod
    async def resolve(self, alert_id: str) -> bool: ...

    @abstractmethod
    def get_active_alerts(self) -> list[Alert]: ...


class EmailAlertProvider(AlertProvider):
    """Reference email alert provider."""

    provider_id = "alerts.email"
    name = "Email Alert Provider"

    def __init__(self, recipients: list[str] | None = None) -> None:
        self._recipients = recipients or ["admin@volta.ai"]
        self._alerts: dict[str, Alert] = {}

    async def fire(self, alert: Alert) -> bool:
        self._alerts[alert.alert_id] = alert
        return True

    async def resolve(self, alert_id: str) -> bool:
        a = self._alerts.get(alert_id)
        if a:
            a.resolved = True
            a.resolved_at = 1786088100.0
            return True
        return False

    def get_active_alerts(self) -> list[Alert]:
        return [a for a in self._alerts.values() if not a.resolved]

    def get_all_alerts(self) -> list[Alert]:
        return list(self._alerts.values())
