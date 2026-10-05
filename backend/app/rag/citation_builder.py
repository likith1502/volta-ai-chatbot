from app.rag.chunk import Chunk
from app.rag.citation import Citation
from app.rag.repository import DocumentRepository


class CitationBuilder:
    """Produces audit Citations from retrieved chunks and document metadata."""

    def __init__(self, document_repository: DocumentRepository) -> None:
        self.document_repository = document_repository

    def build_citations(self, ranked_chunks: list[tuple[Chunk, float]]) -> list[Citation]:
        citations: list[Citation] = []
        for chk, score in ranked_chunks:
            doc = self.document_repository.get_document(chk.document_id)
            title = doc.title if doc else f"Doc {chk.document_id}"
            uri = doc.source.uri_or_path if doc else ""

            cit = Citation(
                document_id=chk.document_id,
                document_title=title,
                page_number=chk.page_number,
                chunk_id=chk.chunk_id,
                snippet=chk.text[:120],
                confidence_score=score,
                source_uri=uri,
            )
            citations.append(cit)
        return citations
