from enum import Enum


class IntegrationStatus(str, Enum):
    """Runtime health status of an integration provider."""

    UNKNOWN = "unknown"
    CONFIGURED = "configured"
    READY = "ready"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    DISCONNECTED = "disconnected"
    FAILED = "failed"
    DISABLED = "disabled"
