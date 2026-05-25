"""Prediction repository for ML outputs."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Prediction
from app.repositories.base_repository import BaseRepository


class PredictionRepository(BaseRepository[Prediction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Prediction)

    async def get_latest_for_defect(self, defect_id: str) -> Prediction | None:
        result = await self.session.execute(
            select(self.model).where(self.model.defect_id == defect_id).order_by(self.model.prediction_date.desc())
        )
        return result.scalar_one_or_none()