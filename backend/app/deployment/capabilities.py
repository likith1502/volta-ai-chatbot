"""Deployment capabilities — feature flags per deployment target."""

from dataclasses import dataclass


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
