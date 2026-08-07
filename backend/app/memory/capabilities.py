from pydantic import BaseModel, Field


class MemoryStorageCapabilities(BaseModel):
    """Storage capabilities flags defining supported repository capabilities."""

    supports_embeddings: bool = False
    supports_search: bool = True
    supports_metadata: bool = True
    supports_filters: bool = True
    supports_hybrid: bool = True
    supports_ttl: bool = True
    supports_pinning: bool = True
