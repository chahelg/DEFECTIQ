"""Upload session repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UploadSession
from app.repositories.base_repository import BaseRepository


class UploadRepository(BaseRepository[UploadSession]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UploadSession)

    async def get_latest_for_file(self, file_name: str) -> UploadSession | None:
        result = await self.session.execute(
            select(self.model).where(self.model.file_name == file_name).order_by(self.model.created_at.desc())
        )
        return result.scalar_one_or_none()