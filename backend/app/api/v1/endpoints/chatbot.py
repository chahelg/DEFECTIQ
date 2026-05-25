"""Chatbot endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import current_user_id, db_session
from app.repositories.chat_repository import ChatRepository
from app.repositories.defect_repository import DefectRepository
from app.schemas import ChatHistoryItem, ChatMessageRequest, ChatMessageResponse, ChatSuggestionsResponse
from app.services.analytics_service import AnalyticsService
from app.services.chatbot_service import ChatbotService
from app.services.nlp_service import NLPService

router = APIRouter(prefix="/chat", tags=["Chatbot"])


def get_chatbot_service(session=Depends(db_session)) -> ChatbotService:
    return ChatbotService(ChatRepository(session), AnalyticsService(DefectRepository(session)), NLPService())


@router.post("/message", response_model=ChatMessageResponse)
async def message(
    payload: ChatMessageRequest,
    user_id: str = Depends(current_user_id),
    service: ChatbotService = Depends(get_chatbot_service),
) -> ChatMessageResponse:
    return await service.chat(payload, user_id)


@router.post("/stream")
async def stream_message(
    payload: ChatMessageRequest,
    user_id: str = Depends(current_user_id),
    service: ChatbotService = Depends(get_chatbot_service),
) -> StreamingResponse:
    return StreamingResponse(service.stream(payload, user_id), media_type="text/event-stream")


@router.get("/history", response_model=list[ChatHistoryItem])
async def history(
    conversation_id: str | None = None,
    user_id: str = Depends(current_user_id),
    service: ChatbotService = Depends(get_chatbot_service),
) -> list[ChatHistoryItem]:
    return await service.history(user_id, conversation_id)


@router.get("/suggestions", response_model=ChatSuggestionsResponse)
async def suggestions(
    query: str = "",
    conversation_id: str | None = None,
    service: ChatbotService = Depends(get_chatbot_service),
) -> ChatSuggestionsResponse:
    return await service.suggestions(query, conversation_id)
