import uuid
from typing import Optional

from pydantic import BaseModel, Field

from app.rag.job_status import JobStatus


class IngestionJob(BaseModel):
    """Background ingestion task tracking document parsing, chunking, embedding, and indexing status."""

    job_id: str = Field(default_factory=lambda: f"job_{uuid.uuid4().hex[:8]}")
    document_id: str
    status: JobStatus = JobStatus.QUEUED
    chunks_created: int = Field(default=0, ge=0)
    embeddings_generated: int = Field(default=0, ge=0)
    error_message: Optional[str] = None
    created_at: float = Field(default_factory=lambda: 1786088000.0)
