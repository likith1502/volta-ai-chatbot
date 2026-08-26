from app.rag.embedding_registry import EmbeddingRegistry
from app.rag.parser_registry import ParserRegistry


class RAGRegistry:
    """Registry maintaining active document parsers, embedding providers, and vector stores."""

    def __init__(self) -> None:
        self.parsers = ParserRegistry()
        self.embeddings = EmbeddingRegistry()
