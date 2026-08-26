from typing import Optional

from app.rag.embedding_provider import EmbeddingProvider, MockEmbeddingProvider


class EmbeddingRegistry:
    """Registry maintaining active vector embedding providers."""

    def __init__(self) -> None:
        self._providers: dict[str, EmbeddingProvider] = {}
        default_p = MockEmbeddingProvider()
        self._providers[default_p.provider_id] = default_p
        self._default_id = default_p.provider_id

    def register_provider(self, provider: EmbeddingProvider) -> None:
        self._providers[provider.provider_id] = provider

    def get_provider(self, provider_id: Optional[str] = None) -> EmbeddingProvider:
        p_id = provider_id or self._default_id
        return self._providers.get(p_id, self._providers[self._default_id])
