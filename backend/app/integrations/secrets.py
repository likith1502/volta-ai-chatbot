import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger("app.integrations.secrets")


class SecretProvider(ABC):
    """Abstract interface for secret resolution and rotation management."""

    @abstractmethod
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        pass

    @abstractmethod
    def refresh_secret(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def invalidate_cache(self) -> None:
        pass

    @abstractmethod
    def secret_version(self, key: str) -> str:
        pass

    @abstractmethod
    def rotate(self, key: str, new_value: str) -> bool:
        pass


class EnvSecretProvider(SecretProvider):
    """Reference implementation resolving secrets from environment variables."""

    def __init__(self) -> None:
        self._cache: dict[str, str] = {}
        self._versions: dict[str, int] = {}

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        if key in self._cache:
            return self._cache[key]
        val = os.getenv(key, default)
        if val is not None:
            self._cache[key] = val
            self._versions[key] = self._versions.get(key, 1)
        return val

    def refresh_secret(self, key: str) -> Optional[str]:
        self._cache.pop(key, None)
        return self.get_secret(key)

    def invalidate_cache(self) -> None:
        self._cache.clear()

    def secret_version(self, key: str) -> str:
        v = self._versions.get(key, 1)
        return f"v{v}"

    def rotate(self, key: str, new_value: str) -> bool:
        os.environ[key] = new_value
        self._cache[key] = new_value
        self._versions[key] = self._versions.get(key, 1) + 1
        logger.info(
            f"EnvSecretProvider rotated secret '{key}' to version {self.secret_version(key)}"
        )
        return True
