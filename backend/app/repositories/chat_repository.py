"""Chat history repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ChatHistory
from app.repositories.base_repository import BaseRepository


class ChatRepository(BaseRepository[ChatHistory]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ChatHistory)

    async def get_by_conversation_id(self, conversation_id: str) -> list[ChatHistory]:
        result = await self.session.execute(
            select(self.model).where(self.model.conversation_id == conversation_id).order_by(self.model.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_recent_by_user(self, user_id: str, limit: int = 25) -> list[ChatHistory]:
        result = await self.session.execute(
            select(self.model).where(self.model.user_id == user_id).order_by(self.model.created_at.desc()).limit(limit)
        )
        return list(reversed(result.scalars().all()))