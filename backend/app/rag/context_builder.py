from app.rag.budget import RetrievalBudget
from app.rag.chunk import Chunk
from app.rag.citation_builder import CitationBuilder
from app.rag.context import RAGContext
from app.rag.repository import DocumentRepository


class RAGContextBuilder:
    """Assembles ranked chunks and citations into formatted RAGContext."""

    def __init__(self, document_repository: DocumentRepository) -> None:
        self.citation_builder = CitationBuilder(document_repository)

    def build_context(self, query: str, ranked_chunks: list[tuple[Chunk, float]], budget: RetrievalBudget) -> RAGContext:
        # Enforce budget limits
        limited = ranked_chunks[: budget.max_chunks]
        citations = self.citation_builder.build_citations(limited)

        parts = []
        scores = []
        for i, (chk, score) in enumerate(limited, 1):
            parts.append(f"--- Context Source [{i}] (Doc: {chk.document_id}, Page: {chk.page_number}, Score: {score}) ---\n{chk.text}")
            scores.append(score)

        formatted_text = "\n\n".join(parts) if parts else "No relevant context found."

        return RAGContext(
            query=query,
            context_text=formatted_text,
            citations=citations[: budget.max_citations],
            scores=scores,
        )
