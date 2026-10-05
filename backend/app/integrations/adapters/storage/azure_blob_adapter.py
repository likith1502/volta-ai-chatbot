import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.storage.storage_adapter import StorageAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.storage.azure_blob")

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_BLOB_AVAILABLE = True
except ImportError:
    BlobServiceClient = None
    AZURE_BLOB_AVAILABLE = False


class AzureBlobStorageAdapter(StorageAdapter):
    """Production Azure Blob Storage Adapter using azure-storage-blob SDK with lazy loading and timeouts."""

    def __init__(
        self,
        container_name: str = "volta-azure-container",
        connect_timeout: float = 5.0,
        request_timeout: float = 15.0,
    ) -> None:
        super().__init__(provider_id="storage.azure_blob", name="Azure Blob Storage Adapter", priority=95)
        self.container_name = container_name
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._service_client: Any = None
        self._container_client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape and resolves secrets without making network calls."""
        if context:
            self._context = context

        conn_str = self._context.resolved_secrets.get("AZURE_STORAGE_CONNECTION_STRING")
        container = self._context.resolved_secrets.get("AZURE_CONTAINER_NAME", self.container_name)
        self.container_name = container

        if not AZURE_BLOB_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("AzureBlobStorageAdapter initialized without azure-storage-blob dependency.")
            return

        if not conn_str:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("AzureBlobStorageAdapter initialized without connection string.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_container_client(self) -> Any:
        """Lazily instantiates Azure Blob Container Client."""
        if not AZURE_BLOB_AVAILABLE:
            raise RuntimeError("azure-storage-blob package is unavailable. Install 'azure-storage-blob' to enable Azure storage.")

        if self._container_client is None:
            conn_str = self._context.resolved_secrets.get("AZURE_STORAGE_CONNECTION_STRING")
            if not conn_str:
                raise ValueError("AZURE_STORAGE_CONNECTION_STRING missing from context secrets.")

            def _init_client():
                service_client = BlobServiceClient.from_connection_string(
                    conn_str, connection_timeout=self.connect_timeout, read_timeout=self.request_timeout
                )
                return service_client.get_container_client(self.container_name)

            self._container_client = await asyncio.to_thread(_init_client)

        return self._container_client

    async def connect(self) -> bool:
        """Verifies readiness without initiating network calls."""
        if not AZURE_BLOB_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        conn_str = self._context.resolved_secrets.get("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically closes Azure Blob client session."""
        if self._container_client is not None:
            def _close():
                if hasattr(self._container_client, "close"):
                    self._container_client.close()

            await asyncio.to_thread(_close)
            self._container_client = None

        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def upload(self, key: str, data: bytes, metadata: Optional[dict[str, Any]] = None) -> str:
        """Uploads binary blob data to Azure Blob container."""
        container_client = await self._get_container_client()

        def _upload():
            blob_client = container_client.get_blob_client(key)
            blob_client.upload_blob(data, overwrite=True, metadata=metadata)
            return f"azure://{self.container_name}/{key}"

        return await asyncio.to_thread(_upload)

    async def download(self, key: str) -> bytes:
        """Downloads binary blob data from Azure Blob container."""
        container_client = await self._get_container_client()

        def _download():
            blob_client = container_client.get_blob_client(key)
            stream = blob_client.download_blob()
            return stream.readall()

        return await asyncio.to_thread(_download)

    async def delete(self, key: str) -> bool:
        """Deletes blob from Azure Blob container."""
        container_client = await self._get_container_client()

        def _delete():
            blob_client = container_client.get_blob_client(key)
            blob_client.delete_blob()
            return True

        return await asyncio.to_thread(_delete)

    async def list_keys(self, prefix: str = "") -> list[str]:
        """Lists blob names in container matching prefix."""
        container_client = await self._get_container_client()

        def _list():
            blobs = container_client.list_blobs(name_starts_with=prefix)
            return [b.name for b in blobs]

        return await asyncio.to_thread(_list)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not AZURE_BLOB_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="AzureBlob",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "azure-storage-blob package not installed"},
            )

        conn_str = self._context.resolved_secrets.get("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="AzureBlob",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "AZURE_STORAGE_CONNECTION_STRING missing from secrets"},
            )

        try:
            container_client = await self._get_container_client()

            def _check():
                container_client.get_container_properties()

            await asyncio.to_thread(_check)
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="AzureBlob",
                is_healthy=True,
                health_level=HealthLevel.GREEN,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"container": self.container_name},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="AzureBlob",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
