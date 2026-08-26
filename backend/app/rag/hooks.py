from abc import ABC, abstractmethod

from app.rag.context import RAGContext
from app.rag.document import Document


class BeforeDocumentIngestHook(ABC):
    @abstractmethod
    async def before_ingest(self, document: Document) -> None:
        pass


class AfterQueryRetrievalHook(ABC):
    @abstractmethod
    async def after_retrieval(self, query: str, context: RAGContext) -> None:
        pass
