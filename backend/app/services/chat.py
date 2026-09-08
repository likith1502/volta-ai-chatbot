import logging
import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIProvider
from app.ai.factory import AIProviderFactory
from app.ai.memory.base import MemoryStrategy
from app.ai.memory.factory import MemoryStrategyFactory
from app.ai.models import AIToolCall
from app.ai.prompts.prompt_builder import PromptBuilder
from app.ai.prompts.recommendation import is_recommendation_requested
from app.ai.tools.dispatcher import AIToolDispatcher
from app.ai.tools.recommendation_tool import RecommendationTool
from app.ai.tools.registry import AIToolRegistry
from app.exceptions.domain import UserNotFoundException
from app.models.enums import ConversationSource, ConversationStatus, MessageRole
from app.models.message import Message
from app.repositories.base import BaseRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.user import UserRepository
from app.services.base import BaseService
from app.services.chat_graph import ChatGraphOrchestrator

logger = logging.getLogger("app.services.chat")


class ChatService(BaseService):
    """Application orchestrator for conversational AI interactions and workflow execution."""

    def __init__(
        self,
        session: AsyncSession,
        provider: Optional[AIProvider] = None,
        memory_strategy: Optional[MemoryStrategy] = None,
        tool_dispatcher: Optional[AIToolDispatcher] = None,
    ) -> None:
        super().__init__(session)
        self.conversation_repo = ConversationRepository(session)
        self.user_repo = UserRepository(session)
        self.message_repo = BaseRepository(Message, session)
        self.provider = provider or AIProviderFactory.get_provider()
        self.memory_strategy = memory_strategy or MemoryStrategyFactory.get_strategy()
        self.prompt_builder = PromptBuilder()

        # Tool Execution Framework Initialization
        if tool_dispatcher:
            self.tool_dispatcher = tool_dispatcher
        else:
            registry = AIToolRegistry()
            registry.register(RecommendationTool(session))
            self.tool_dispatcher = AIToolDispatcher(registry)

        self.graph_orchestrator = ChatGraphOrchestrator(
            provider=self.provider,
            tool_dispatcher=self.tool_dispatcher,
            prompt_builder=self.prompt_builder,
        )

    async def process_chat(
        self,
        user_id: uuid.UUID,
        session_id: str,
        message_text: str,
    ) -> dict[str, Any]:
        """Orchestrates an authenticated user chat turn through the refined enterprise pipeline."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID '{user_id}' not found.")

        conv = await self.conversation_repo.get_by_session_id(session_id)
        if not conv:
            conv = await self.conversation_repo.create(
                {
                    "user_id": user_id,
                    "session_id": session_id,
                    "source": ConversationSource.WEB,
                    "status": ConversationStatus.ACTIVE,
                    "title": message_text[:30] if message_text else "New Chat",
                }
            )

        # 1. Save User Message
        msg_count = await self.message_repo.count()
        await self.message_repo.create(
            {
                "conversation_id": conv.id,
                "role": MessageRole.USER,
                "content": message_text,
                "sequence_number": msg_count + 1,
            }
        )

        # 2. Memory Strategy Retrieval
        memories = await self.memory_strategy.retrieve_memories(self.session, conv.id, limit=10)

        # 3. Fetch Recent Conversation History
        stmt = (
            select(Message)
            .where(Message.conversation_id == conv.id, Message.is_deleted == False)  # noqa: E712
            .order_by(Message.created_at.asc())
            .limit(20)
        )
        res = await self.session.execute(stmt)
        history_messages = list(res.scalars().all())

        # 4. Execute Chat Turn via Graph Runtime with Safe Fallback
        ai_content: str
        ai_model: str
        token_count: int
        usage_data: dict[str, Any]
        recommendation_id: Optional[uuid.UUID] = None

        try:
            graph_turn = await self.graph_orchestrator.execute_chat_turn(
                conversation_id=conv.id,
                user_id=user_id,
                session_id=session_id,
                message_text=message_text,
                history_messages=history_messages,
                memories=memories,
            )
            ai_content = graph_turn["content"]
            ai_model = graph_turn["model_used"]
            token_count = graph_turn["total_tokens"]
            usage_data = graph_turn["usage"]
            recommendation_id = graph_turn["recommendation_id"]
        except Exception as graph_err:
            logger.warning(
                "Graph runtime execution failed, falling back to direct pipeline: %s",
                graph_err,
                exc_info=True,
            )
            # Direct Proven Fallback Path
            ai_request = self.prompt_builder.build(
                user_input=message_text,
                conversation_history=history_messages,
                memories=memories,
            )
            ai_response = await self.provider.generate_response(ai_request)

            if ai_response.tool_calls:
                for call in ai_response.tool_calls:
                    call.arguments["conversation_id"] = str(conv.id)
                    tool_res = await self.tool_dispatcher.dispatch(call)
                    if tool_res.success and tool_res.data and "recommendation_id" in tool_res.data:
                        recommendation_id = tool_res.data["recommendation_id"]
            elif is_recommendation_requested(message_text):
                tool_call = AIToolCall(
                    tool_name="recommendation",
                    arguments={"conversation_id": str(conv.id), "user_query": message_text},
                )
                tool_res = await self.tool_dispatcher.dispatch(tool_call)
                if tool_res.success and tool_res.data and "recommendation_id" in tool_res.data:
                    recommendation_id = tool_res.data["recommendation_id"]

            ai_content = ai_response.content
            ai_model = ai_response.model_used
            token_count = ai_response.usage.total_tokens
            usage_data = ai_response.usage.model_dump()

        # 5. Save Assistant Response Turn
        assistant_msg = await self.message_repo.create(
            {
                "conversation_id": conv.id,
                "role": MessageRole.ASSISTANT,
                "content": ai_content,
                "model_used": ai_model,
                "token_count": token_count,
                "sequence_number": msg_count + 2,
            }
        )

        # 6. Commit Transaction Boundary
        await self.commit()

        return {
            "conversation_id": conv.id,
            "session_id": session_id,
            "message": assistant_msg,
            "recommendation_id": recommendation_id,
            "usage": usage_data,
        }
