"""Chatbot orchestration service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, AsyncIterator

from app.chatbot.engine import AskYourDefectsEngine
from app.chatbot.memory import ConversationMemory
from app.chatbot.query_parser import QueryParser
from app.repositories.chat_repository import ChatRepository
from app.services.analytics_service import AnalyticsService
from app.services.nlp_service import NLPService
from app.schemas import ChatHistoryItem, ChatMessageRequest, ChatMessageResponse, ChatSuggestionsResponse


class ChatbotService:
    def __init__(
        self,
        chat_repository: ChatRepository,
        analytics_service: AnalyticsService,
        nlp_service: NLPService | None = None,
    ) -> None:
        self.chat_repository = chat_repository
        self.analytics_service = analytics_service
        self.nlp_service = nlp_service or NLPService()
        self.memory = ConversationMemory(chat_repository)
        self.engine = AskYourDefectsEngine(analytics_service, self.nlp_service, self.memory)

    async def chat(self, payload: ChatMessageRequest, user_id: str) -> ChatMessageResponse:
        reply = await self.engine.build_reply(user_id, payload.conversation_id, payload.message, payload.context_filters)
        return ChatMessageResponse(
            conversation_id=reply.conversation_id,
            message_id=__import__("uuid").uuid4(),
            response=reply.content,
            confidence=reply.confidence,
            sources=reply.sources,
            generated_at=datetime.now(timezone.utc),
            intent=reply.intent,
            chart_data=reply.chart_data,
            follow_up_questions=reply.follow_up_questions,
            response_markdown=reply.content,
            metadata=reply.metadata,
        )

    async def stream(self, payload: ChatMessageRequest, user_id: str) -> AsyncIterator[str]:
        async for chunk in self.engine.stream_reply(user_id, payload.conversation_id, payload.message, payload.context_filters):
            yield chunk

    async def history(self, user_id: str, conversation_id: str | None = None) -> list[ChatHistoryItem]:
        if conversation_id:
            history = await self.chat_repository.get_by_conversation_id(conversation_id)
        else:
            history = await self.chat_repository.get_recent_by_user(user_id)
        return [
            ChatHistoryItem(
                id=item.id,
                conversation_id=item.conversation_id or "",
                message_type=item.message_type or "assistant",
                message_content=item.message_content,
                sources_used=item.sources_used,
                confidence_score=item.confidence_score,
                created_at=item.created_at,
            )
            for item in history
        ]

    async def suggestions(self, query: str, conversation_id: str | None = None) -> ChatSuggestionsResponse:
        return ChatSuggestionsResponse(conversation_id=conversation_id, suggestions=await self.engine.suggestions(query))