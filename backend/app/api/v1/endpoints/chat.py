"""Phase 2 chat endpoints."""

from __future__ import annotations

from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.dependencies import current_user_id, db_session
from app.models import ChatHistory
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


def _parse_user_uuid(user_id: str) -> UUID:
    try:
        return UUID(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication context") from exc


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None


@router.post("/message")
async def message(payload: ChatMessageRequest, session=Depends(db_session), user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    return await ChatService.handle_message(payload.message, session, conversation_id=payload.conversation_id, user_id=user_id)


@router.get("/history")
async def history(conversation_id: str | None = None, session=Depends(db_session), user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    user_uuid = _parse_user_uuid(user_id)
    query = select(ChatHistory).where(ChatHistory.user_id == user_uuid)
    if conversation_id:
        query = query.where(ChatHistory.conversation_id == conversation_id)
    result = await session.execute(query.order_by(ChatHistory.created_at.asc()))
    messages = [
        {
            "conversation_id": str(item.conversation_id),
            "role": item.role,
            "content": item.content,
            "intent": item.intent,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
        for item in result.scalars().all()
    ]
    return {"messages": messages}


@router.get("/suggestions")
async def suggestions(query: str = "", session=Depends(db_session), user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    user_uuid = _parse_user_uuid(user_id)
    recent = await session.execute(select(ChatHistory).where(ChatHistory.user_id == user_uuid).order_by(ChatHistory.created_at.desc()).limit(3))
    prompts = [item.content[:80] for item in recent.scalars().all()]
    if query:
        prompts.insert(0, f"Ask about {query}")
    return {"suggestions": prompts or ["Summarize the latest defects", "Show the highest risk tickets", "What is blocking resolution?"]}
