from enum import Enum
from pydantic import BaseModel, Field


class DocumentSource(str, Enum):
    """Supported document source types."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    HTML = "html"
    MARKDOWN = "markdown"
    CSV = "csv"
    CUSTOM = "custom"


class DocumentSourceLocator(BaseModel):
    """Location metadata for a document source."""

    source_type: DocumentSource = DocumentSource.TXT
    uri_or_path: str = Field(default="")
    file_size_bytes: int = Field(default=0, ge=0)
