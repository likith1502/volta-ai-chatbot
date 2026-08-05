import time
import uuid
from typing import Optional

from app.checkpoints.checkpoint_filter import CheckpointFilter
from app.checkpoints.checkpoint_manager import CheckpointManager
from app.checkpoints.checkpoint_status import ReplayAction, ReplayMode
from app.checkpoints.exceptions import ReplayValidationException
from app.checkpoints.replay_context import ReplayContext
from app.checkpoints.replay_history import ReplayHistory
from app.checkpoints.replay_metrics import ReplayMetrics
from app.checkpoints.replay_result import ReplayResult
from app.checkpoints.replay_strategy import ReplayStrategy, SequentialReplayStrategy
from app.context.state import ConversationState


class ReplayEngine:
    """
    Core Provider-Independent Replay Framework.
    Replays execution checkpoint history, simulates step progression, resumes execution from checkpoints,
    and maintains audit lineage without mutating original ConversationState objects.
    """

    def __init__(
        self,
        manager: Optional[CheckpointManager] = None,
        strategy: Optional[ReplayStrategy] = None,
    ) -> None:
        self.manager = manager or CheckpointManager()
        self.strategy = strategy or SequentialReplayStrategy()
        self.history = ReplayHistory()
        self.metrics = ReplayMetrics()

    async def replay(
        self,
        workflow_id: str,
        strategy: Optional[ReplayStrategy] = None,
        mode: ReplayMode = ReplayMode.FULL,
    ) -> ReplayResult:
        """Replays all stored checkpoints for a workflow_id."""
        start_time = time.perf_counter()
        cps = self.manager.list_checkpoints(CheckpointFilter(workflow_id=workflow_id))
        if not cps:
            raise ReplayValidationException(
                f"No checkpoints found for workflow_id '{workflow_id}' to replay."
            )

        active_strategy = strategy or self.strategy
        context = ReplayContext(replay_mode=mode)

        if cps:
            self.history.record_action(cps[0].checkpoint_id, ReplayAction.START, {"mode": mode.value})

        result = await active_strategy.execute_replay(cps, context)

        if cps:
            self.history.record_action(cps[-1].checkpoint_id, ReplayAction.FINISH)

        duration = round(time.perf_counter() - start_time, 4)
        self.metrics.replayed_steps += len(cps)
        self.metrics.checkpoint_count = len(cps)
        self.metrics.replay_duration += duration
        self.metrics.compute_success_rate(failed_steps=len(result.errors))

        return result

    async def resume(self, checkpoint_id: uuid.UUID) -> ConversationState:
        """Restores ConversationState snapshot from checkpoint for resuming execution."""
        state = self.manager.restore_checkpoint(checkpoint_id)
        self.history.record_action(checkpoint_id, ReplayAction.RESUME)
        return state

    async def restart(self, workflow_id: str) -> ConversationState:
        """Restores ConversationState from the earliest checkpoint matching workflow_id."""
        cps = self.manager.list_checkpoints(CheckpointFilter(workflow_id=workflow_id))
        if not cps:
            raise ReplayValidationException(
                f"No checkpoints found for workflow_id '{workflow_id}' to restart."
            )
        earliest_cp = min(cps, key=lambda c: c.timestamp)
        self.history.record_action(earliest_cp.checkpoint_id, ReplayAction.RESTART)
        return earliest_cp.state_snapshot

    async def simulate(self, workflow_id: str) -> ReplayResult:
        """Simulates replay in SIMULATION mode without state side effects."""
        return await self.replay(workflow_id=workflow_id, mode=ReplayMode.SIMULATION)
