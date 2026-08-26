class RAGError(Exception):
    """Base exception for all RAG Engine errors."""

    pass


class DocumentNotFoundError(RAGError):
    """Raised when a document ID cannot be found."""

    pass


class IngestionError(RAGError):
    """Raised when document ingestion or parsing fails."""

    pass


class RetrievalError(RAGError):
    """Raised when context retrieval or vector search fails."""

    pass
