import logging
from typing import Any

from app.rag.chunk import Chunk
from app.rag.chunk_strategy import ChunkStrategy

logger = logging.getLogger("app.rag.chunker")


class DocumentChunker:
    """Splits document text into un-embedded text Chunk instances according to ChunkStrategy."""

    def __init__(self) -> None:
        pass

    def chunk_document(
        self,
        document_id: str,
        text: str,
        strategy: ChunkStrategy = ChunkStrategy.FIXED,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        metadata: dict[str, Any] = None,
    ) -> list[Chunk]:
        if not text.strip():
            return []

        chunks: list[Chunk] = []
        meta = metadata or {}

        if strategy in [ChunkStrategy.FIXED, ChunkStrategy.SLIDING_WINDOW]:
            step = max(1, chunk_size - chunk_overlap)
            start = 0
            page = 1
            while start < len(text):
                end = min(len(text), start + chunk_size)
                slice_text = text[start:end].strip()
                if slice_text:
                    tokens = len(slice_text.split())
                    chk = Chunk(
                        document_id=document_id,
                        page_number=page,
                        text=slice_text,
                        token_count=tokens,
                        metadata=dict(meta),
                    )
                    chunks.append(chk)
                start += step
                page += 1
        elif strategy == ChunkStrategy.PARAGRAPH:
            paragraphs = text.split("\n\n")
            for i, p in enumerate(paragraphs, 1):
                p_str = p.strip()
                if p_str:
                    tokens = len(p_str.split())
                    chunks.append(
                        Chunk(
                            document_id=document_id,
                            page_number=i,
                            text=p_str,
                            token_count=tokens,
                            metadata=dict(meta),
                        )
                    )
        else:
            # Fallback sentence/semantic splitting
            lines = text.split("\n")
            for i, line in enumerate(lines, 1):
                l_str = line.strip()
                if l_str:
                    tokens = len(l_str.split())
                    chunks.append(
                        Chunk(
                            document_id=document_id,
                            page_number=i,
                            text=l_str,
                            token_count=tokens,
                            metadata=dict(meta),
                        )
                    )

        logger.info(
            f"DocumentChunker split document '{document_id}' into {len(chunks)} chunks using strategy '{strategy.value}'"
        )
        return chunks
