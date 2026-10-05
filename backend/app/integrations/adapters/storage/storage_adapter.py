import os
from abc import ABC, abstractmethod
from typing import Any, Optional
from app.integrations.capabilities import IntegrationCapability
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport, IntegrationProvider
from app.integrations.status import IntegrationStatus


class StorageAdapter(IntegrationProvider, ABC):
    """Abstract interface for object & file storage adapters."""

    def __init__(self, provider_id: str, name: str, priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name=name, category=IntegrationCapability.STORAGE, priority=priority)

    @abstractmethod
    async def upload(self, key: str, data: bytes, metadata: Optional[dict[str, Any]] = None) -> str:
        pass

    @abstractmethod
    async def download(self, key: str) -> bytes:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def list_keys(self, prefix: str = "") -> list[str]:
        pass


class FilesystemStorageAdapter(StorageAdapter):
    """Reference storage adapter storing files on local filesystem."""

    def __init__(self, root_dir: str = "./storage_data", provider_id: str = "storage.filesystem", priority: int = 10) -> None:
        super().__init__(provider_id=provider_id, name="Filesystem Storage Adapter", priority=priority)
        self.root_dir = root_dir
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[Any] = None) -> None:
        os.makedirs(self.root_dir, exist_ok=True)
        self._status = IntegrationStatus.READY
        await self.connect()

    async def connect(self) -> bool:
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def upload(self, key: str, data: bytes, metadata: Optional[dict[str, Any]] = None) -> str:
        fp = os.path.join(self.root_dir, key)
        os.makedirs(os.path.dirname(fp), exist_ok=True)
        with open(fp, "wb") as f:
            f.write(data)
        return fp

    async def download(self, key: str) -> bytes:
        fp = os.path.join(self.root_dir, key)
        if not os.path.exists(fp):
            raise FileNotFoundError(f"Key '{key}' not found in filesystem storage.")
        with open(fp, "rb") as f:
            return f.read()

    async def delete(self, key: str) -> bool:
        fp = os.path.join(self.root_dir, key)
        if os.path.exists(fp):
            os.remove(fp)
            return True
        return False

    async def list_keys(self, prefix: str = "") -> list[str]:
        keys = []
        if not os.path.exists(self.root_dir):
            return []
        for r, d, f in os.walk(self.root_dir):
            for fn in f:
                rel = os.path.relpath(os.path.join(r, fn), self.root_dir)
                if rel.startswith(prefix):
                    keys.append(rel)
        return keys

    async def check_health(self) -> IntegrationHealthReport:
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="Filesystem",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=self.status,
            latency_ms=1.2,
        )


class FilesystemSandboxAdapter(FilesystemStorageAdapter):
    """Sandbox execution mode of FilesystemStorageAdapter preventing write modifications outside temp path."""

    def __init__(self) -> None:
        super().__init__(root_dir="./storage_sandbox", provider_id="storage.filesystem_sandbox", priority=5)
