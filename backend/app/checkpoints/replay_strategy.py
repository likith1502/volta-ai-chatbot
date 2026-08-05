import time
from abc import ABC, abstractmethod
from typing import List, Optional

from app.checkpoints.checkpoint import Checkpoint
from app.checkpoints.replay_context import ReplayContext
from app.checkpoints.replay_result import ReplayResult
from app.execution.execution_snapshot import ExecutionSnapshot


class ReplayStrategy(ABC):
    """Abstract interface for checkpoint replay execution strategies."""

    @abstractmethod
    async def execute_replay(
        self,
        checkpoints: List[Checkpoint],
        context: ReplayContext,
    ) -> ReplayResult:
        """Executes replay across the provided checkpoint list according to the strategy."""
        pass


class SequentialReplayStrategy(ReplayStrategy):
    """Replays checkpoints in forward chronological order."""

    async def execute_replay(
        self,
        checkpoints: List[Checkpoint],
        context: ReplayContext,
    ) -> ReplayResult:
        start_time = time.perf_counter()
        sorted_cps = sorted(checkpoints, key=lambda c: c.timestamp)

        visited_snapshots: List[ExecutionSnapshot] = []
        final_state = None

        for cp in sorted_cps:
            context.current_step += 1
            if cp.execution_snapshot:
                visited_snapshots.append(cp.execution_snapshot)
            final_state = cp.state_snapshot

        duration = round(time.perf_counter() - start_time, 4)

        return ReplayResult(
            success=True,
            final_state=final_state,
            visited_snapshots=visited_snapshots,
            execution_time=duration,
        )


class ReverseReplayStrategy(ReplayStrategy):
    """Contract placeholder for reverse order execution replay."""

    async def execute_replay(
        self,
        checkpoints: List[Checkpoint],
        context: ReplayContext,
    ) -> ReplayResult:
        sorted_cps = sorted(checkpoints, key=lambda c: c.timestamp, reverse=True)
        snapshots = [c.execution_snapshot for c in sorted_cps if c.execution_snapshot]
        final_state = sorted_cps[0].state_snapshot if sorted_cps else None
        return ReplayResult(success=True, final_state=final_state, visited_snapshots=snapshots)


class StepReplayStrategy(ReplayStrategy):
    """Contract placeholder for single-step execution replay."""

    async def execute_replay(
        self,
        checkpoints: List[Checkpoint],
        context: ReplayContext,
    ) -> ReplayResult:
        cp = checkpoints[0] if checkpoints else None
        snapshot = [cp.execution_snapshot] if cp and cp.execution_snapshot else []
        final_state = cp.state_snapshot if cp else None
        return ReplayResult(success=True, final_state=final_state, visited_snapshots=snapshot)
