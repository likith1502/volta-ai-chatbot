import logging
from typing import Optional

from app.rag.job import IngestionJob
from app.rag.job_status import JobStatus

logger = logging.getLogger("app.rag.job_manager")


class JobManager:
    """Manages document ingestion jobs and status reporting."""

    def __init__(self) -> None:
        self._jobs: dict[str, IngestionJob] = {}

    def create_job(self, document_id: str) -> IngestionJob:
        job = IngestionJob(document_id=document_id, status=JobStatus.QUEUED)
        self._jobs[job.job_id] = job
        logger.info(f"IngestionJob '{job.job_id}' created for document '{document_id}'")
        return job

    def get_job(self, job_id: str) -> Optional[IngestionJob]:
        return self._jobs.get(job_id)

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        chunks: int = 0,
        embeddings: int = 0,
        error: Optional[str] = None,
    ) -> None:
        job = self.get_job(job_id)
        if job:
            job.status = status
            job.chunks_created = chunks
            job.embeddings_generated = embeddings
            job.error_message = error
            logger.info(f"IngestionJob '{job_id}' status updated to {status.value}")
