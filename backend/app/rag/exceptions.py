class RAGException(Exception):
    """Base exception for all RAG Engine errors."""

    pass


class DocumentNotFoundError(RAGException):
    """Raised when a document ID cannot be found."""

    pass


class IngestionError(RAGException):
    """Raised when document ingestion or parsing fails."""

    pass


class RetrievalError(RAGException):
    """Raised when context retrieval or vector search fails."""

    pass
