import asyncio
import logging
import time
from typing import Any, Optional

from app.integrations.adapters.storage.storage_adapter import StorageAdapter
from app.integrations.context import IntegrationContext
from app.integrations.health_level import HealthLevel
from app.integrations.provider import IntegrationHealthReport
from app.integrations.status import IntegrationStatus

logger = logging.getLogger("app.integrations.adapters.storage.s3")

try:
    import boto3
    from botocore.config import Config as BotoConfig
    from botocore.exceptions import BotoCoreError, ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    boto3 = None
    BotoConfig = None
    BotoCoreError = Exception
    ClientError = Exception
    BOTO3_AVAILABLE = False


class S3StorageAdapter(StorageAdapter):
    """Production AWS S3 Storage Adapter using boto3 with lazy loading, timeouts, retries, and secret redaction."""

    def __init__(
        self,
        bucket: str = "volta-s3-bucket",
        region: str = "us-east-1",
        connect_timeout: float = 5.0,
        request_timeout: float = 15.0,
        max_retries: int = 3,
    ) -> None:
        super().__init__(provider_id="storage.s3", name="AWS S3 Storage Adapter", priority=100)
        self.bucket = bucket
        self.region = region
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self._s3_client: Any = None
        self._status = IntegrationStatus.CONFIGURED

    async def initialize(self, context: Optional[IntegrationContext] = None) -> None:
        """Validates configuration shape and resolves secrets without making external network calls."""
        if context:
            self._context = context

        aws_key = self._context.resolved_secrets.get("AWS_ACCESS_KEY_ID")
        aws_secret = self._context.resolved_secrets.get("AWS_SECRET_ACCESS_KEY")
        aws_region = self._context.resolved_secrets.get("AWS_REGION", self.region)
        s3_bucket = self._context.resolved_secrets.get("AWS_S3_BUCKET", self.bucket)

        self.region = aws_region
        self.bucket = s3_bucket

        self._status = IntegrationStatus.READY
        if BOTO3_AVAILABLE and aws_key and aws_secret:
            self._health_level = HealthLevel.GREEN
        else:
            self._health_level = HealthLevel.ORANGE if not aws_key else HealthLevel.RED

    async def _get_client(self) -> Any:
        """Lazily instantiates boto3 S3 client."""
        if not BOTO3_AVAILABLE:
            raise RuntimeError("boto3 package is unavailable. Install 'boto3' to enable AWS S3 storage.")

        if self._s3_client is None:
            aws_key = self._context.resolved_secrets.get("AWS_ACCESS_KEY_ID")
            aws_secret = self._context.resolved_secrets.get("AWS_SECRET_ACCESS_KEY")

            if not aws_key or not aws_secret:
                raise ValueError("AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) missing from context secrets.")

            boto_config = BotoConfig(
                connect_timeout=self.connect_timeout,
                read_timeout=self.request_timeout,
                retries={"max_attempts": self.max_retries, "mode": "standard"},
                region_name=self.region,
            )

            def _create_client():
                return boto3.client(
                    "s3",
                    aws_access_key_id=aws_key,
                    aws_secret_access_key=aws_secret,
                    config=boto_config,
                )

            self._s3_client = await asyncio.to_thread(_create_client)

        return self._s3_client

    async def connect(self) -> bool:
        """Verifies readiness without initiating unnecessary network handshakes."""
        self._status = IntegrationStatus.CONNECTED
        return True

    async def disconnect(self) -> bool:
        """Deterministically closes boto3 S3 client session."""
        if self._s3_client is not None:
            def _close():
                if hasattr(self._s3_client, "close"):
                    self._s3_client.close()

            await asyncio.to_thread(_close)
            self._s3_client = None

        self._status = IntegrationStatus.DISCONNECTED
        return True

    async def upload(self, key: str, data: bytes, metadata: Optional[dict[str, Any]] = None) -> str:
        """Uploads binary object data to S3."""
        client = await self._get_client()
        extra_args: dict[str, Any] = {}
        if metadata:
            extra_args["Metadata"] = {str(k): str(v) for k, v in metadata.items()}

        def _put():
            client.put_object(Bucket=self.bucket, Key=key, Body=data, **extra_args)
            return f"s3://{self.bucket}/{key}"

        return await asyncio.to_thread(_put)

    async def download(self, key: str) -> bytes:
        """Downloads binary object data from S3."""
        client = await self._get_client()

        def _get():
            res = client.get_object(Bucket=self.bucket, Key=key)
            return res["Body"].read()

        return await asyncio.to_thread(_get)

    async def delete(self, key: str) -> bool:
        """Deletes object from S3 bucket."""
        client = await self._get_client()

        def _del():
            client.delete_object(Bucket=self.bucket, Key=key)
            return True

        return await asyncio.to_thread(_del)

    async def list_keys(self, prefix: str = "") -> list[str]:
        """Lists object keys in bucket matching prefix."""
        client = await self._get_client()

        def _list():
            res = client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            contents = res.get("Contents", [])
            return [obj["Key"] for obj in contents]

        return await asyncio.to_thread(_list)

    async def check_health(self) -> IntegrationHealthReport:
        """Performs lightweight, timeout-bounded health check."""
        start_time = time.perf_counter()

        if not BOTO3_AVAILABLE:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="S3",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=0.0,
                details={"error": "dependency_unavailable", "message": "boto3 package not installed"},
            )

        aws_key = self._context.resolved_secrets.get("AWS_ACCESS_KEY_ID")
        if not aws_key:
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="S3",
                is_healthy=False,
                health_level=HealthLevel.ORANGE,
                status=IntegrationStatus.CONFIGURED,
                latency_ms=0.0,
                details={"error": "credentials_missing", "message": "AWS_ACCESS_KEY_ID missing from secrets"},
            )

        try:
            client = await self._get_client()

            def _head_bucket():
                client.head_bucket(Bucket=self.bucket)

            await asyncio.to_thread(_head_bucket)
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="S3",
                is_healthy=True,
                health_level=HealthLevel.GREEN,
                status=IntegrationStatus.CONNECTED,
                latency_ms=round(latency, 2),
                details={"bucket": self.bucket, "region": self.region},
            )
        except Exception as exc:
            latency = (time.perf_counter() - start_time) * 1000.0
            return IntegrationHealthReport(
                provider_id=self.provider_id,
                provider_name=self.name,
                provider_type="S3",
                is_healthy=False,
                health_level=HealthLevel.RED,
                status=IntegrationStatus.DEGRADED,
                latency_ms=round(latency, 2),
                details={"error": "connection_failure", "message": str(exc)},
            )
