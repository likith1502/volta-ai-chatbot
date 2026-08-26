from enum import Enum


class RankingStrategy(str, Enum):
    """Supported reranking strategies."""

    COSINE = "cosine"
    HYBRID = "hybrid"
    BM25 = "bm25"
    WEIGHTED = "weighted"
    RECENCY = "recency"
    METADATA = "metadata"
    CROSS_ENCODER = "cross_encoder"
