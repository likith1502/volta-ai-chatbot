from typing import Any, Optional

from app.integrations.adapters.storage.storage_adapter import StorageAdapter
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus


class S3StorageAdapter(StorageAdapter):
    """Extension placeholder for AWS S3 Storage Adapter."""

    def __init__(self, bucket: str = "volta-s3-bucket") -> None:
        super().__init__(
            provider_id="storage.s3", name="AWS S3 Storage Adapter", priority=100
        )
        self.bucket = bucket
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[Any] = None) -> None:
        self._status = IntegrationStatus.READY

    async def connect(self) -> bool:
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def upload(
        self, key: str, data: bytes, metadata: Optional[dict[str, Any]] = None
    ) -> str:
        return f"s3://{self.bucket}/{key}"

    async def download(self, key: str) -> bytes:
        return b"S3 mock data"

    async def delete(self, key: str) -> bool:
        return True

    async def list_keys(self, prefix: str = "") -> list[str]:
        return [f"{prefix}file1.txt"]

    async def check_health(self) -> IntegrationHealthReport:
        return IntegrationHealthReport(
            provider_id=self.provider_id,
            provider_name=self.name,
            provider_type="S3",
            is_healthy=True,
            health_level=HealthLevel.GREEN,
            status=self.status,
            latency_ms=15.5,
        )


class AzureBlobStorageAdapter(S3StorageAdapter):
    """Extension placeholder for Azure Blob Storage Adapter."""

    def __init__(self) -> None:
        super().__init__(bucket="volta-azure-container")
        self._provider_id = "storage.azure_blob"
        self._name = "Azure Blob Storage Adapter"


class GCSStorageAdapter(S3StorageAdapter):
    """Extension placeholder for Google Cloud Storage Adapter."""

    def __init__(self) -> None:
        super().__init__(bucket="volta-gcs-bucket")
        self._provider_id = "storage.gcs"
        self._name = "Google Cloud Storage Adapter"
