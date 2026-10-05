import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.storage.storage_adapter import StorageAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.storage.gcs")

try:
    from google.cloud import storage as gcs_storage
    GCS_AVAILABLE = True
except ImportError:
    gcs_storage = None
    GCS_AVAILABLE = False


class GCSStorageAdapter(StorageAdapter):
    """Production Google Cloud Storage Adapter using google-cloud-storage SDK with lazy loading and timeouts."""

    def __init__(
        self,
        bucket_name: str = "volta-gcs-bucket",
        connect_timeout: float = 5.0,
        request_timeout: float = 15.0,
    ) -> None:
        super().__init__(provider_id="storage.gcs", name="Google Cloud Storage Adapter", priority=90)
        self.bucket_name = bucket_name
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self._storage_client: Any = None
        self._bucket: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape and resolves secrets without making network calls."""
        if context:
            self._context = context

        project_id = self._context.resolved_secrets.get("GCP_PROJECT_ID")
        bucket = self._context.resolved_secrets.get("GCS_BUCKET_NAME", self.bucket_name)
        self.bucket_name = bucket

        if not GCS_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            self._health_level = HealthLevel.RED
            logger.warning("GCSStorageAdapter initialized without google-cloud-storage dependency.")
            return

        if not project_id:
            self._status = IntegrationStatus.CONFIGURED
            self._health_level = HealthLevel.ORANGE
            logger.info("GCSStorageAdapter initialized without GCP_PROJECT_ID.")
            return

        self._status = IntegrationStatus.READY
        self._health_level = HealthLevel.GREEN

    async def _get_bucket(self) -> Any:
        """Lazily instantiates GCS Client and Bucket."""
        if not GCS_AVAILABLE:
            raise RuntimeError("google-cloud-storage package is unavailable. Install 'google-cloud-storage' to enable GCS storage.")

        if self._bucket is None:
            project_id = self._context.resolved_secrets.get("GCP_PROJECT_ID")
            if not project_id:
                raise ValueError("GCP_PROJECT_ID missing from context secrets.")

            def _init():
                client = gcs_storage.Client(project=project_id)
                return client.bucket(self.bucket_name)

            self._bucket = await asyncio.to_thread(_init)

        return self._bucket

    async def connect(self) -> bool:
        """Verifies readiness without initiating network calls."""
        if not GCS_AVAILABLE:
            self._status = IntegrationStatus.DEGRADED
            return False
        project_id = self._context.resolved_secrets.get("GCP_PROJECT_ID")
        if not project_id:
            self._status = IntegrationStatus.CONFIGURED
            return False
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically resets GCS client session."""
        self._bucket = None
        self._storage_client = None
        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def upload(self, key: str, data: bytes, metadata: Optional[dict[str, Any]] = None) -> str:
        """Uploads object data to GCS bucket."""
        bucket = await self._get_bucket()

        def _upload():
            blob = bucket.blob(key)
            if metadata:
                blob.metadata = {str(k): str(v) for k, v in metadata.items()}
            blob.upload_from_string(data, timeout=self.request_timeout)
            return f"gs://{self.bucket_name}/{key}"

        return await asyncio.to_thread(_upload)

    async def download(self, key: str) -> bytes:
        """Downloads object data from GCS bucket."""
        bucket = await self._get_bucket()

        def _download():
            blob = bucket.blob(key)
            return blob.download_as_bytes(timeout=self.request_timeout)

        return await asyncio.to_thread(_download)

    async def delete(self, key: str) -> bool:
        """Deletes object from GCS bucket."""
        bucket = await self._get_bucket()

        def _delete():
            blob = bucket.blob(key)
            blob.delete(timeout=self.request_timeout)
            return True

        return await asyncio.to_thread(_delete)

    async def list_keys(self, prefix: str = "") -> list[str]:
        """Lists object keys in GCS bucket matching prefix."""
        bucket = await self._get_bucket()

        def _list():
            blobs = bucket.list_blobs(prefix=prefix, timeout=self.request_timeout)
            return [b.name for b in blobs]

        return await asyncio.to_thread(_list)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight health check."""
        start_time = time.perf_counter()

        if not GCS_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="GCS",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "google-cloud-storage package not installed"},
            )

        project_id = self._context.resolved_secrets.get("GCP_PROJECT_ID")
        if not project_id:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="GCS",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "GCP_PROJECT_ID missing from secrets"},
            )

        try:
            bucket = await self._get_bucket()

            def _check():
                bucket.exists(timeout=self.connect_timeout)

            await asyncio.to_thread(_check)
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="GCS",
                is_healthy=True,
                health_level=HealthLevel.GREEN,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"bucket": self.bucket_name, "project_id": project_id},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="GCS",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
