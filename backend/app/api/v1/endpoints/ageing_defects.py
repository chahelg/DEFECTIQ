"""Ageing defects endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.ageing_defects_service import AgeingDefectsService

router = APIRouter(prefix="/ageing-defects", tags=["Ageing Defects"])


async def get_service(session: AsyncSession = Depends(get_db)) -> AgeingDefectsService:
    return AgeingDefectsService(session)


@router.get("/snapshot")
async def get_ageing_snapshot(service: AgeingDefectsService = Depends(get_service)) -> dict:
    return await service.get_snapshot()
