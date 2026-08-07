from enum import Enum


class JobStatus(str, Enum):
    """Ingestion job status enum."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
