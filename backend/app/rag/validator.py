from app.rag.document import Document
from app.rag.exceptions import RAGException


class RAGValidator:
    """Validates document formatting and query inputs."""

    @staticmethod
    def validate_document(document: Document) -> bool:
        if not document.title.strip():
            raise RAGException("Document title cannot be empty.")
        if not document.raw_text.strip():
            raise RAGException("Document text content cannot be empty.")
        return True
