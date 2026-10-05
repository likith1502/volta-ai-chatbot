"""Consolidated Models Module for Integrations Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from enum import Enum
from pydantic import BaseModel, Field
from typing import Any

# --- Consolidated from health_level.py ---
class HealthLevel(str, Enum):
    """Operational health level classification."""
    GREEN = 'green'
    YELLOW = 'yellow'
    ORANGE = 'orange'
    RED = 'red'

# --- Consolidated from status.py ---
class IntegrationStatus(str, Enum):
    """Runtime health status of an integration provider."""
    UNKNOWN = 'unknown'
    CONFIGURED = 'configured'
    READY = 'ready'
    CONNECTED = 'connected'
    DEGRADED = 'degraded'
    DISCONNECTED = 'disconnected'
    FAILED = 'failed'
    DISABLED = 'disabled'

# --- Consolidated from metadata.py ---
class IntegrationMetadata(BaseModel):
    """Adapter metadata payload."""
    provider_id: str
    name: str
    category: str
    adapter_version: str = '1.0.0'
    minimum_platform_version: str = '7.0.0'
    maximum_platform_version: str = '8.0.0'
    author: str = 'VOLTA Engineering'
    extra: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from policy.py ---
class IntegrationPolicy(BaseModel):
    """Security and execution policy for integration adapters."""
    allow_sandbox_override: bool = True
    enforce_tls: bool = True
    require_secret_resolution: bool = True

# --- Consolidated from provider_config.py ---
class ProviderConfig(BaseModel):
    """Adapter-specific configuration container."""
    provider_id: str
    enabled: bool = True
    priority: int = Field(default=10, ge=1)
    weight: float = Field(default=1.0, ge=0.0)
    preferred: bool = False
    options: dict[str, Any] = Field(default_factory=dict)

# --- Consolidated from runtime_config.py ---
class IntegrationRuntimeConfig(BaseModel):
    """Runtime execution bounds and timeout settings."""
    connection_timeout_seconds: float = Field(default=5.0, ge=0.1)
    health_check_interval_seconds: float = Field(default=30.0, ge=1.0)
    max_reconnect_attempts: int = Field(default=3, ge=1)

