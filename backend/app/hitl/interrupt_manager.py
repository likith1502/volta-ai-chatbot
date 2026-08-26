import uuid
from typing import Any, Dict


class InterruptManager:
    """Orchestration manager defining contracts for execution interruptions and pause gates."""

    def interrupt_execution(
        self,
        execution_id: uuid.UUID,
        node_id: str,
        reason: str = "Human approval required",
    ) -> Dict[str, Any]:
        """Interprets and signals an execution interruption contract."""
        return {
            "execution_id": str(execution_id),
            "node_id": node_id,
            "interrupted": True,
            "status": "interrupted",
            "reason": reason,
        }

    def pause_execution(self, execution_id: uuid.UUID) -> Dict[str, Any]:
        """Signals execution pause contract."""
        return {
            "execution_id": str(execution_id),
            "status": "paused",
            "paused": True,
        }

    def resume_execution(self, execution_id: uuid.UUID) -> Dict[str, Any]:
        """Signals execution resume contract."""
        return {
            "execution_id": str(execution_id),
            "status": "resumed",
            "resumed": True,
        }

    def cancel_execution(
        self, execution_id: uuid.UUID, reason: str = ""
    ) -> Dict[str, Any]:
        """Signals execution cancellation contract."""
        return {
            "execution_id": str(execution_id),
            "status": "cancelled",
            "cancelled": True,
            "reason": reason,
        }
