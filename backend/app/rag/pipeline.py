import logging

from app.rag.ingestion_runtime import IngestionRuntime
from app.rag.query_runtime import QueryRuntime

logger = logging.getLogger("app.rag.pipeline")


class RAGPipeline:
    """Encapsulates RAG IngestionRuntime and QueryRuntime operations."""

    def __init__(
        self, ingestion_runtime: IngestionRuntime, query_runtime: QueryRuntime
    ) -> None:
        self.ingestion = ingestion_runtime
        self.query = query_runtime
