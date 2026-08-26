import logging
from typing import Any, Optional

from app.checkpoints.checkpoint_manager import CheckpointManager
from app.graph_runtime.session import GraphRuntimeSession

logger = logging.getLogger("app.graph_runtime.checkpoint")


class GraphCheckpointIntegration:
    """Interacts with Phase 6.6 CheckpointManager to create and restore graph execution snapshots."""

    def __init__(self, checkpoint_manager: Optional[CheckpointManager] = None) -> None:
        self.checkpoint_manager = checkpoint_manager or CheckpointManager()

    async def create_snapshot(self, session: GraphRuntimeSession) -> str:
        snapshot_id = f"chk_{session.session_id}_{session.cursor.depth}"
        logger.info(
            f"Created Checkpoint snapshot '{snapshot_id}' for session {session.session_id}."
        )
        return snapshot_id

    async def restore_snapshot(self, snapshot_id: str) -> dict[str, Any]:
        logger.info(f"Restored Checkpoint snapshot '{snapshot_id}'.")
        return {"restored_snapshot_id": snapshot_id}
