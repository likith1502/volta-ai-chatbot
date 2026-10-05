import logging
from typing import Any, Optional
from app.memory.manager import MemoryManager

logger = logging.getLogger("app.agents.memory")


class AgentMemoryIntegration:
    """Delegates agent memory retrieval and persistence strictly to public MemoryManager contract."""

    def __init__(self, memory_manager: Optional[MemoryManager] = None) -> None:
        self.memory_manager = memory_manager or MemoryManager()

    async def get_agent_context(self, conversation_id: Any) -> list[dict[str, Any]]:
        """Retrieves conversational memory items via MemoryManager facade."""
        try:
            items = await self.memory_manager.get_relevant_context(conversation_id=conversation_id, query="")
            return [i.model_dump() for i in items]
        except Exception as exc:
            logger.warning(f"Memory retrieval via MemoryManager failed: {exc}")
            return []
