import uuid
from typing import List, Optional

from app.checkpoints.checkpoint import Checkpoint
from app.checkpoints.checkpoint_filter import CheckpointFilter
from app.checkpoints.checkpoint_metadata import CheckpointMetadata
from app.checkpoints.checkpoint_policy import CheckpointPolicy
from app.checkpoints.checkpoint_status import CheckpointStatus
from app.checkpoints.checkpoint_store import CheckpointStore, InMemoryCheckpointStore
from app.checkpoints.checkpoint_validation import CheckpointValidationResult
from app.context.state import ConversationState
from app.execution.execution_snapshot import ExecutionSnapshot


class CheckpointManager:
    """
    Manager for creating, restoring, archiving, deleting, and validating execution checkpoints.
    Uses an underlying CheckpointStore and applies CheckpointPolicy rules.
    """

    def __init__(
        self,
        store: Optional[CheckpointStore] = None,
        policy: Optional[CheckpointPolicy] = None,
    ) -> None:
        self.store = store or InMemoryCheckpointStore()
        self.policy = policy or CheckpointPolicy()

    def create_checkpoint(
        self,
        workflow_id: str,
        graph_id: str,
        state: ConversationState,
        execution_snapshot: Optional[ExecutionSnapshot] = None,
        metadata: Optional[CheckpointMetadata] = None,
        status: CheckpointStatus = CheckpointStatus.ACTIVE,
    ) -> Checkpoint:
        """Creates and persists an immutable Checkpoint instance."""
        cp = Checkpoint(
            workflow_id=workflow_id,
            graph_id=graph_id,
            state_snapshot=state,
            execution_snapshot=execution_snapshot,
            status=status,
            metadata=metadata or CheckpointMetadata(),
        )
        self.store.save(cp)
        return cp

    def restore_checkpoint(self, checkpoint_id: uuid.UUID) -> ConversationState:
        """Retrieves checkpoint by ID and returns restored ConversationState snapshot."""
        cp = self.store.load(checkpoint_id)
        if self.policy.validation_required:
            val_res = self.validate_checkpoint(checkpoint_id)
            if not val_res.is_valid:
                raise ValueError(f"Cannot restore invalid checkpoint '{checkpoint_id}': {val_res.errors}")
        return cp.state_snapshot

    def delete_checkpoint(self, checkpoint_id: uuid.UUID) -> None:
        """Removes checkpoint by ID."""
        self.store.delete(checkpoint_id)

    def list_checkpoints(self, filter: Optional[CheckpointFilter] = None) -> List[Checkpoint]:
        """Lists checkpoints matching filter criteria."""
        all_checkpoints = self.store.list()
        if filter is None:
            return all_checkpoints
        return [cp for cp in all_checkpoints if filter.matches(cp)]

    def validate_checkpoint(self, checkpoint_id: uuid.UUID) -> CheckpointValidationResult:
        """Validates checkpoint structural integrity and returns CheckpointValidationResult."""
        try:
            cp = self.store.load(checkpoint_id)
            errors = []
            warnings = []

            if not cp.workflow_id:
                errors.append("Checkpoint workflow_id is empty.")
            if not cp.graph_id:
                errors.append("Checkpoint graph_id is empty.")
            if cp.state_snapshot is None:
                errors.append("Checkpoint state_snapshot is None.")

            is_valid = len(errors) == 0
            return CheckpointValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                version_match=True,
                integrity_passed=is_valid,
                compatible=is_valid,
            )
        except Exception as exc:
            return CheckpointValidationResult(
                is_valid=False,
                errors=[str(exc)],
                version_match=False,
                integrity_passed=False,
                compatible=False,
            )

    def archive_checkpoint(self, checkpoint_id: uuid.UUID) -> Checkpoint:
        """Archives a checkpoint by ID."""
        existing = self.store.load(checkpoint_id)
        archived_cp = Checkpoint(
            checkpoint_id=existing.checkpoint_id,
            execution_id=existing.execution_id,
            workflow_id=existing.workflow_id,
            graph_id=existing.graph_id,
            state_snapshot=existing.state_snapshot,
            execution_snapshot=existing.execution_snapshot,
            timestamp=existing.timestamp,
            status=CheckpointStatus.ARCHIVED,
            metadata=existing.metadata,
        )
        self.store.save(archived_cp)
        return archived_cp
