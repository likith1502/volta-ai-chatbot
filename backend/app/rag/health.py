from pydantic import BaseModel, Field

from app.rag.repository import DocumentRepository
from app.rag.vector_repository import VectorRepository


class RAGHealthStatus(BaseModel):
    is_healthy: bool = True
    documents_count: int = Field(default=0, ge=0)
    vectors_count: int = Field(default=0, ge=0)
    status: str = "Enterprise RAG Engine operational"
    components: dict[str, str] = Field(
        default_factory=lambda: {
            "ingestion_runtime": "healthy",
            "query_runtime": "healthy",
            "vector_repository": "healthy",
            "document_repository": "healthy",
            "cache": "healthy",
        }
    )


class RAGHealthManager:
    def __init__(
        self,
        document_repository: DocumentRepository,
        vector_repository: VectorRepository,
    ) -> None:
        self.doc_repo = document_repository
        self.vec_repo = vector_repository

    async def check_health(self) -> RAGHealthStatus:
        doc_count = len(self.doc_repo.list_documents())
        vec_count = await self.vec_repo.count()
        return RAGHealthStatus(
            is_healthy=True,
            documents_count=doc_count,
            vectors_count=vec_count,
            status="Enterprise RAG Engine operational",
        )
