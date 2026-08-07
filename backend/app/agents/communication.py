import logging
from typing import Optional
from app.agents.mailbox import AgentMailbox
from app.agents.message import AgentMessage
from app.events.event import WorkflowEvent
from app.events.event_bus import WorkflowEventBus

logger = logging.getLogger("app.agents.communication")


class CommunicationManager:
    """Orchestrates inter-agent messaging, mailboxes, and event-driven notifications via WorkflowEventBus."""

    def __init__(self, event_bus: Optional[WorkflowEventBus] = None) -> None:
        self.event_bus = event_bus or WorkflowEventBus()
        self._mailboxes: dict[str, AgentMailbox] = {}

    def get_or_create_mailbox(self, agent_id: str) -> AgentMailbox:
        if agent_id not in self._mailboxes:
            self._mailboxes[agent_id] = AgentMailbox(agent_id)
        return self._mailboxes[agent_id]

    async def send_message(self, message: AgentMessage) -> None:
        mailbox = self.get_or_create_mailbox(message.recipient_agent_id)
        mailbox.receive(message)

        # Publish event-driven notification
        try:
            await self.event_bus.publish(
                WorkflowEvent(
                    event_name="agent_message.sent",
                    payload={
                        "message_id": message.message_id,
                        "sender_id": message.sender_agent_id,
                        "recipient_id": message.recipient_agent_id,
                        "type": message.message_type,
                    },
                    source="communication_manager",
                )
            )
        except Exception:
            pass

    async def broadcast(self, sender_id: str, content: str, recipient_ids: list[str]) -> None:
        for recipient_id in recipient_ids:
            msg = AgentMessage(
                sender_agent_id=sender_id,
                recipient_agent_id=recipient_id,
                content=content,
            )
            await self.send_message(msg)
