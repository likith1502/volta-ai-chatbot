from typing import Optional
from app.rag.parser import BaseDocumentParser, TextDocumentParser


class ParserRegistry:
    """Registry maintaining document parsers by MIME type."""

    def __init__(self) -> None:
        self._parsers: list[BaseDocumentParser] = [TextDocumentParser()]

    def register_parser(self, parser: BaseDocumentParser) -> None:
        self._parsers.append(parser)

    def get_parser_for_mime(self, mime_type: str) -> Optional[BaseDocumentParser]:
        for p in self._parsers:
            if p.supports_mime_type(mime_type):
                return p
        return self._parsers[0]  # Fallback text parser
