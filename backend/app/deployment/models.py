"""Consolidated Models Module for Deployment Package."""
from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import Any
import re

# --- Consolidated from capabilities.py ---
@dataclass
class DeploymentCapabilities:
    supports_rolling: bool = True
    supports_blue_green: bool = True
    supports_canary: bool = True
    supports_horizontal_scaling: bool = True
    supports_vertical_scaling: bool = True
    supports_auto_scaling: bool = True
    supports_zero_downtime: bool = True
    supports_backup: bool = True
    supports_disaster_recovery: bool = True
    supports_health_checks: bool = True
    supports_observability: bool = True
    supports_secrets_rotation: bool = True
    supports_multi_region: bool = False
    supports_gpu: bool = False

# --- Consolidated from config.py ---
@dataclass
class DeploymentConfig:
    """Global deployment configuration."""
    platform_version: str = '7.8.0'
    default_environment: str = 'production'
    default_strategy: str = 'rolling'
    default_image_tag: str = 'latest'
    registry_url: str = 'ghcr.io/likith1502/volta-ai-chatbot'
    health_check_interval_seconds: int = 30
    deployment_timeout_seconds: int = 300
    rollback_on_validation_failure: bool = True
    enable_auto_scaling: bool = True
    enable_backup: bool = True
    enable_dr: bool = True
    enable_observability: bool = True
    extra: dict[str, Any] = field(default_factory=dict)

# --- Consolidated from context.py ---
@dataclass
class DeploymentContext:
    deployment_id: str = ''
    environment: str = 'production'
    platform_version: str = '7.8.0'
    operator: str = 'system'
    dry_run: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

# --- Consolidated from policy.py ---
@dataclass
class DeploymentPolicy:
    require_validation_before_deploy: bool = True
    require_backup_before_deploy: bool = True
    rollback_on_health_failure: bool = True
    allow_production_deploy_without_staging: bool = False
    enforce_semantic_versioning: bool = True
    max_canary_weight_pct: int = 50
    min_healthy_replicas_before_scale_down: int = 1
    auto_rollback_on_error_rate_pct: float = 5.0
    deployment_freeze_enabled: bool = False
    deployment_freeze_reason: str = ''

# --- Consolidated from versioning.py ---
@dataclass
class SemVer:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, version: str) -> 'SemVer':
        m = re.match('^(\\d+)\\.(\\d+)\\.(\\d+)$', version)
        if not m:
            raise ValueError(f'Invalid semver: {version}')
        return cls(major=int(m.group(1)), minor=int(m.group(2)), patch=int(m.group(3)))

    def __str__(self) -> str:
        return f'{self.major}.{self.minor}.{self.patch}'

    def __lt__(self, other: 'SemVer') -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def is_compatible_with(self, other: 'SemVer') -> bool:
        """True if same major version."""
        return self.major == other.major

    def next_patch(self) -> 'SemVer':
        return SemVer(self.major, self.minor, self.patch + 1)

    def next_minor(self) -> 'SemVer':
        return SemVer(self.major, self.minor + 1, 0)

    def next_major(self) -> 'SemVer':
        return SemVer(self.major + 1, 0, 0)

