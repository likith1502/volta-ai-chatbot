from typing import Any

from app.rag.chunk import Chunk


class MetadataFilter:
    """Filters chunks based on metadata constraints."""

    @staticmethod
    def filter_chunks(chunks: list[Chunk], filters: dict[str, Any]) -> list[Chunk]:
        if not filters:
            return chunks
        results = []
        for c in chunks:
            match = True
            for k, v in filters.items():
                if c.metadata.get(k) != v:
                    match = False
                    break
            if match:
                results.append(c)
        return results
