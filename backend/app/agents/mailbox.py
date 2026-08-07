import logging
from typing import Optional
from app.agents.message import AgentMessage

logger = logging.getLogger("app.agents.mailbox")


class AgentMailbox:
    """Mailbox container storing inbox and outbox messages for an agent."""

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        self._inbox: list[AgentMessage] = []
        self._outbox: list[AgentMessage] = []

    def receive(self, message: AgentMessage) -> None:
        self._inbox.append(message)
        logger.debug(f"Agent '{self.agent_id}' received message '{message.message_id}'")

    def pop_next(self) -> Optional[AgentMessage]:
        if self._inbox:
            return self._inbox.pop(0)
        return None

    def list_inbox(self) -> list[AgentMessage]:
        return list(self._inbox)

    def list_outbox(self) -> list[AgentMessage]:
        return list(self._outbox)
