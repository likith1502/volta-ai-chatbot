"""Storage Adapter Re-exports for Backward Compatibility."""

from app.integrations.adapters.storage.s3_adapter import S3StorageAdapter
from app.integrations.adapters.storage.azure_blob_adapter import AzureBlobStorageAdapter
from app.integrations.adapters.storage.gcs_adapter import GCSStorageAdapter

__all__ = [
    "S3StorageAdapter",
    "AzureBlobStorageAdapter",
    "GCSStorageAdapter",
]
