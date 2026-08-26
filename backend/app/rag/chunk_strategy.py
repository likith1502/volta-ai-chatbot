from enum import Enum


class ChunkStrategy(str, Enum):
    """Strategies for splitting document text into chunks."""

    FIXED = "fixed"
    SLIDING_WINDOW = "sliding_window"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    SEMANTIC = "semantic"
