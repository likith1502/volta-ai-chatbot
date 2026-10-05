from abc import ABC, abstractmethod
from typing import Optional
from app.rag.chunk import Chunk
from app.rag.document import Document


class DocumentRepository(ABC):
    """Abstract repository for storing Document metadata, raw content, and Chunk records."""

    @abstractmethod
    def save_document(self, document: Document) -> None:
        pass

    @abstractmethod
    def get_document(self, document_id: str) -> Optional[Document]:
        pass

    @abstractmethod
    def list_documents(self) -> list[Document]:
        pass

    @abstractmethod
    def delete_document(self, document_id: str) -> bool:
        pass

    @abstractmethod
    def save_chunks(self, chunks: list[Chunk]) -> None:
        pass

    @abstractmethod
    def get_chunks(self, document_id: str) -> list[Chunk]:
        pass

    @abstractmethod
    def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        pass
