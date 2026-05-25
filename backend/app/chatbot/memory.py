"""Conversational memory backed by PostgreSQL chat history."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.repositories.chat_repository import ChatRepository


@dataclass(slots=True)
class MemoryTurn:
    role: str
    content: str
    sources: list[dict[str, Any]] | None = None


class ConversationMemory:
    def __init__(self, chat_repository: ChatRepository) -> None:
        self.chat_repository = chat_repository

    async def load(self, conversation_id: str, limit: int = 8) -> list[MemoryTurn]:
        history = await self.chat_repository.get_by_conversation_id(conversation_id)
        turns: list[MemoryTurn] = []
        for item in history[-limit:]:
            turns.append(MemoryTurn(role=item.message_type or "assistant", content=item.message_content, sources=item.sources_used))
        return turns

    async def append(self, conversation_id: str, user_id: str, role: str, content: str, *, sources: list[dict[str, Any]] | None = None, confidence: float | None = None, context_defect_ids: list[str] | None = None, context_filters: dict[str, Any] | None = None) -> None:
        await self.chat_repository.create(
            {
                "user_id": user_id,
                "conversation_id": conversation_id,
                "message_type": role,
                "message_content": content,
                "context_defect_ids": context_defect_ids,
                "context_filters": context_filters,
                "sources_used": sources,
                "confidence_score": confidence,
            }
        )

    def new_conversation_id(self) -> str:
        return str(uuid4())
