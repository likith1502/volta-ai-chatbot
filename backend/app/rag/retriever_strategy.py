from enum import Enum


class RetrievalStrategy(str, Enum):
    """Supported retrieval strategies."""

    TOP_K = "top_k"
    HYBRID = "hybrid"
    KEYWORD = "keyword"
    VECTOR = "vector"
    METADATA_FILTER = "metadata_filter"
