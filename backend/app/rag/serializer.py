from app.rag.context import RAGContext
from app.rag.document import Document


class RAGSerializer:
    @staticmethod
    def document_to_json(document: Document) -> str:
        return document.model_dump_json(indent=2)

    @staticmethod
    def context_to_json(context: RAGContext) -> str:
        return context.model_dump_json(indent=2)
