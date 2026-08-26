"""Environment Manager — Development, Testing, Staging, Production environments."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DISASTER_RECOVERY = "disaster_recovery"


@dataclass
class EnvironmentConfig:
    """Configuration bundle for a deployment environment."""

    database_url: str = "postgresql+asyncpg://localhost/volta_dev"
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    debug_mode: bool = False
    replica_count: int = 1
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:3000"])
    feature_flags: dict[str, bool] = field(default_factory=dict)
    secrets_backend: str = "env"
    telemetry_enabled: bool = True
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Environment:
    """Full environment definition."""

    env_id: str
    env_type: EnvironmentType
    name: str
    config: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    is_active: bool = False
    created_at: float = 1786088000.0
    tags: dict[str, str] = field(default_factory=dict)


_DEFAULT_ENVIRONMENTS: dict[EnvironmentType, Environment] = {
    EnvironmentType.DEVELOPMENT: Environment(
        env_id="env_dev",
        env_type=EnvironmentType.DEVELOPMENT,
        name="Development",
        config=EnvironmentConfig(log_level="DEBUG", debug_mode=True),
        is_active=False,
    ),
    EnvironmentType.TESTING: Environment(
        env_id="env_test",
        env_type=EnvironmentType.TESTING,
        name="Testing",
        config=EnvironmentConfig(log_level="DEBUG", debug_mode=False, replica_count=1),
        is_active=False,
    ),
    EnvironmentType.STAGING: Environment(
        env_id="env_staging",
        env_type=EnvironmentType.STAGING,
        name="Staging",
        config=EnvironmentConfig(log_level="INFO", replica_count=2),
        is_active=False,
    ),
    EnvironmentType.PRODUCTION: Environment(
        env_id="env_prod",
        env_type=EnvironmentType.PRODUCTION,
        name="Production",
        config=EnvironmentConfig(log_level="WARNING", replica_count=3),
        is_active=True,
    ),
    EnvironmentType.DISASTER_RECOVERY: Environment(
        env_id="env_dr",
        env_type=EnvironmentType.DISASTER_RECOVERY,
        name="Disaster Recovery",
        config=EnvironmentConfig(log_level="WARNING", replica_count=2),
        is_active=False,
    ),
}


class EnvironmentManager:
    """Manages deployment environments, promotion, and configuration snapshots."""

    def __init__(self) -> None:
        self._environments: dict[EnvironmentType, Environment] = dict(
            _DEFAULT_ENVIRONMENTS
        )
        self._active_env: EnvironmentType = EnvironmentType.PRODUCTION

    def get_environment(self, env_type: EnvironmentType) -> Optional[Environment]:
        return self._environments.get(env_type)

    def list_environments(self) -> list[Environment]:
        return list(self._environments.values())

    def activate(self, env_type: EnvironmentType) -> bool:
        env = self._environments.get(env_type)
        if not env:
            return False
        for e in self._environments.values():
            e.is_active = False
        env.is_active = True
        self._active_env = env_type
        return True

    @property
    def active_environment(self) -> Optional[Environment]:
        return self._environments.get(self._active_env)

    def update_config(
        self, env_type: EnvironmentType, config: EnvironmentConfig
    ) -> bool:
        env = self._environments.get(env_type)
        if not env:
            return False
        env.config = config
        return True

    def get_feature_flag(self, env_type: EnvironmentType, flag: str) -> bool:
        env = self._environments.get(env_type)
        if not env:
            return False
        return env.config.feature_flags.get(flag, False)
