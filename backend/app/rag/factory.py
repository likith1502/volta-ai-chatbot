from app.rag.document import Document
from app.rag.source import DocumentSource, DocumentSourceLocator


class RAGFactory:
    """Factory helper creating Document instances from text, markdown, or PDF sources."""

    @staticmethod
    def create_document(title: str, text: str, mime_type: str = "text/plain", source_uri: str = "") -> Document:
        src = DocumentSourceLocator(
            source_type=DocumentSource.TXT if mime_type == "text/plain" else DocumentSource.MARKDOWN,
            uri_or_path=source_uri,
            file_size_bytes=len(text.encode("utf-8")),
        )
        return Document(title=title, raw_text=text, mime_type=mime_type, source=src)
