import logging
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger("app.graph_runtime.interrupt")


class GraphInterruptSignal(BaseModel):
    """Interrupt signal container for Human-in-the-Loop governance approvals."""

    interrupt_id: str
    node_id: str
    reason: str = "HITL Approval Required"
    requires_human_review: bool = True
    approval_granted: Optional[bool] = None


class GraphInterruptIntegration:
    """Interacts with Phase 6.8 HITL ApprovalManager, ResumeManager, and InterruptManager."""

    async def raise_interrupt(self, node_id: str, reason: str) -> GraphInterruptSignal:
        sig = GraphInterruptSignal(
            interrupt_id=f"int_{node_id}",
            node_id=node_id,
            reason=reason,
        )
        logger.info(f"Raised Graph Interrupt for node '{node_id}': {reason}")
        return sig
