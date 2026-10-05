from app.prompt.templates.base_template import BasePromptTemplate


class RAGPromptTemplate(BasePromptTemplate):
    """Placeholder template contract for Phase 7.6 RAG Engine context injection."""

    @property
    def template_type(self) -> str:
        return "rag"
