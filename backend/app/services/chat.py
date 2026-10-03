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
from app.ai.tools.booking_tool import BookingTool
from app.ai.tools.dispatcher import AIToolDispatcher
from app.ai.tools.recommendation_tool import RecommendationTool
from app.ai.tools.registry import AIToolRegistry
from app.exceptions.domain import UserNotFoundException
from app.models.enums import ConversationSource, ConversationStatus, MessageRole
from app.models.message import Message
from app.models.recommendation import Recommendation
from app.repositories.base import BaseRepository
from app.repositories.conversation import ConversationRepository
from app.repositories.user import UserRepository
from app.services.base import BaseService
from app.services.chat_graph import ChatGraphOrchestrator
from app.services.saved_location import LocationResolver, SavedLocationService

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
        self.saved_location_service = SavedLocationService(session)
        self.location_resolver = LocationResolver(self.saved_location_service)
        self.provider = provider or AIProviderFactory.get_provider()
        self.memory_strategy = memory_strategy or MemoryStrategyFactory.get_strategy()
        self.prompt_builder = PromptBuilder()

        # Tool Execution Framework Initialization
        if tool_dispatcher:
            self.tool_dispatcher = tool_dispatcher
        else:
            registry = AIToolRegistry()
            registry.register(RecommendationTool(session))
            registry.register(BookingTool(session))
            self.tool_dispatcher = AIToolDispatcher(registry)

        self.graph_orchestrator = ChatGraphOrchestrator(
            provider=self.provider,
            tool_dispatcher=self.tool_dispatcher,
            prompt_builder=self.prompt_builder,
            location_resolver=self.location_resolver,
        )

    async def _apply_quoted_fares(
        self, graph_turn: dict[str, Any], recommendation_id: Optional[uuid.UUID]
    ) -> None:
        """Store the fares Gemini showed into the persisted quote.

        The booking reads its fare from the stored quote, so this keeps the
        price the customer saw and the price that gets booked the same.
        """
        overrides = graph_turn.get("fare_overrides") or {}
        if not overrides:
            return
        rec_id = recommendation_id
        if rec_id is None:
            final_state = graph_turn.get("final_state")
            ride = (
                final_state.memory.extracted_entities.get("ride")
                if final_state is not None
                else None
            ) or {}
            raw = ride.get("recommendation_id")
            try:
                rec_id = uuid.UUID(str(raw)) if raw else None
            except (ValueError, TypeError):
                rec_id = None
        if rec_id is None:
            return
        try:
            rec = await self.session.get(Recommendation, rec_id)
            if rec is None:
                return
            data = dict(rec.recommendation_data or {})
            data["options"] = [
                {
                    **opt,
                    "fare": overrides.get(
                        str(opt.get("tier", "")).lower(), opt.get("fare")
                    ),
                }
                for opt in data.get("options", [])
            ]
            data["fare_source"] = "assistant_estimate"
            rec.recommendation_data = data
            await self.session.flush()
        except Exception as exc:  # noqa: BLE001 - never block the reply
            logger.warning("Could not store quoted fares: %s", exc)

    async def process_chat(
        self,
        user_id: uuid.UUID,
        session_id: str,
        message_text: str,
        source: Optional[ConversationSource] = None,
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
                    "source": source or ConversationSource.WEB,
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
        memories = await self.memory_strategy.retrieve_memories(
            self.session, conv.id, limit=10
        )

        # 3. Retrieve User Saved Locations for Deterministic Resolution & Turn Context
        saved_locations = await self.saved_location_service.list_saved_locations(
            user_id
        )

        # 4. Fetch Recent Conversation History
        stmt = (
            select(Message)
            .where(Message.conversation_id == conv.id, Message.is_deleted == False)  # noqa: E712
            .order_by(Message.created_at.asc())
            .limit(20)
        )
        res = await self.session.execute(stmt)
        history_messages = list(res.scalars().all())

        # 5. Execute Chat Turn via Graph Runtime with Safe Fallback
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
                saved_locations=saved_locations,
            )
            ai_content = graph_turn["content"]
            ai_model = graph_turn["model_used"]
            token_count = graph_turn["total_tokens"]
            usage_data = graph_turn["usage"]
            recommendation_id = graph_turn["recommendation_id"]
            await self._apply_quoted_fares(graph_turn, recommendation_id)
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
                saved_locations=saved_locations,
            )
            ai_response = await self.provider.generate_response(ai_request)

            if ai_response.tool_calls:
                for call in ai_response.tool_calls:
                    call.arguments["conversation_id"] = str(conv.id)
                    tool_res = await self.tool_dispatcher.dispatch(call)
                    if (
                        tool_res.success
                        and tool_res.data
                        and "recommendation_id" in tool_res.data
                    ):
                        recommendation_id = tool_res.data["recommendation_id"]
            elif is_recommendation_requested(message_text):
                tool_call = AIToolCall(
                    tool_name="recommendation",
                    arguments={
                        "conversation_id": str(conv.id),
                        "user_query": message_text,
                    },
                )
                tool_res = await self.tool_dispatcher.dispatch(tool_call)
                if (
                    tool_res.success
                    and tool_res.data
                    and "recommendation_id" in tool_res.data
                ):
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

    async def resolve_user_location(
        self,
        user_id: uuid.UUID,
        label_query: str,
    ):
        """Resolves user landmark location deterministically for ride workflows."""
        return await self.location_resolver.resolve(user_id, label_query)
