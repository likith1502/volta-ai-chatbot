import logging
from enum import Enum

logger = logging.getLogger("app.rag.lifecycle")


class DocumentLifecycleState(str, Enum):
    """Lifecycle states of a document within the RAG Engine."""

    UPLOADED = "uploaded"
    PARSING = "parsing"
    CHUNKED = "chunked"
    INDEXED = "indexed"
    READY = "ready"
    ARCHIVED = "archived"
    DELETED = "deleted"


class DocumentLifecycleManager:
    """Manages document state transitions across the RAG ingestion lifecycle."""

    def __init__(
        self, initial_state: DocumentLifecycleState = DocumentLifecycleState.UPLOADED
    ) -> None:
        self.current_state = initial_state

    def transition_to(self, target_state: DocumentLifecycleState) -> bool:
        valid_transitions = {
            DocumentLifecycleState.UPLOADED: [
                DocumentLifecycleState.PARSING,
                DocumentLifecycleState.DELETED,
            ],
            DocumentLifecycleState.PARSING: [
                DocumentLifecycleState.CHUNKED,
                DocumentLifecycleState.DELETED,
            ],
            DocumentLifecycleState.CHUNKED: [
                DocumentLifecycleState.INDEXED,
                DocumentLifecycleState.DELETED,
            ],
            DocumentLifecycleState.INDEXED: [
                DocumentLifecycleState.READY,
                DocumentLifecycleState.DELETED,
            ],
            DocumentLifecycleState.READY: [
                DocumentLifecycleState.ARCHIVED,
                DocumentLifecycleState.DELETED,
            ],
            DocumentLifecycleState.ARCHIVED: [
                DocumentLifecycleState.READY,
                DocumentLifecycleState.DELETED,
            ],
            DocumentLifecycleState.DELETED: [],
        }

        allowed = valid_transitions.get(self.current_state, [])
        if target_state in allowed:
            logger.info(
                f"Document lifecycle transitioned: {self.current_state.value} -> {target_state.value}"
            )
            self.current_state = target_state
            return True
        else:
            logger.warning(
                f"Invalid document lifecycle transition attempt: {self.current_state.value} -> {target_state.value}"
            )
            return False
