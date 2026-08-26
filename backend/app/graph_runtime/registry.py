from typing import Optional

from app.graph_runtime.session import GraphRuntimeSession


class GraphSessionRegistry:
    """Registry holding active GraphRuntimeSession instances in memory."""

    def __init__(self) -> None:
        self._sessions: dict[str, GraphRuntimeSession] = {}

    def register(self, session: GraphRuntimeSession) -> None:
        self._sessions[str(session.session_id)] = session

    def get(self, session_id: str) -> Optional[GraphRuntimeSession]:
        return self._sessions.get(str(session_id))

    def remove(self, session_id: str) -> bool:
        return self._sessions.pop(str(session_id), None) is not None

    def list_all(self) -> list[GraphRuntimeSession]:
        return list(self._sessions.values())
