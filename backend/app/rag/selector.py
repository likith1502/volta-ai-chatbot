from app.rag.chunk import Chunk


class ChunkSelector:
    """Selects target chunks based on relevance scores and limits."""

    @staticmethod
    def select_top_chunks(
        chunks: list[tuple[Chunk, float]], limit: int = 5
    ) -> list[Chunk]:
        return [c for c, _ in chunks[:limit]]
