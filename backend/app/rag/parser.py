from abc import ABC, abstractmethod
from typing import Any
from app.rag.document import Document


class BaseDocumentParser(ABC):
    """Abstract interface for document parsers."""

    @abstractmethod
    def supports_mime_type(self, mime_type: str) -> bool:
        pass

    @abstractmethod
    def parse(self, raw_text: str, metadata: dict[str, Any]) -> str:
        pass


class TextDocumentParser(BaseDocumentParser):
    """Reference parser for plain text and markdown documents."""

    def supports_mime_type(self, mime_type: str) -> bool:
        return mime_type.startswith("text/") or mime_type in ["application/json", "text/markdown"]

    def parse(self, raw_text: str, metadata: dict[str, Any]) -> str:
        # Strip leading/trailing whitespace
        return raw_text.strip()
