from typing import Optional

from app.rag.chunk import Chunk
from app.rag.document import Document
from app.rag.repository import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    """In-memory reference implementation of DocumentRepository."""

    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}
        self._chunks: dict[str, Chunk] = {}

    def save_document(self, document: Document) -> None:
        self._documents[document.document_id] = document

    def get_document(self, document_id: str) -> Optional[Document]:
        return self._documents.get(document_id)

    def list_documents(self) -> list[Document]:
        return list(self._documents.values())

    def delete_document(self, document_id: str) -> bool:
        if document_id in self._documents:
            del self._documents[document_id]
            # remove associated chunks
            to_del = [
                cid for cid, c in self._chunks.items() if c.document_id == document_id
            ]
            for cid in to_del:
                del self._chunks[cid]
            return True
        return False

    def save_chunks(self, chunks: list[Chunk]) -> None:
        for c in chunks:
            self._chunks[c.chunk_id] = c

    def get_chunks(self, document_id: str) -> list[Chunk]:
        return [c for c in self._chunks.values() if c.document_id == document_id]

    def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        return self._chunks.get(chunk_id)
