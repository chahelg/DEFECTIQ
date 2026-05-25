"""Dashboard analytics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.defect_repository import DefectRepository

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_repository(session: AsyncSession = Depends(get_db)) -> DefectRepository:
    return DefectRepository(session)


@router.get("/kpis")
async def get_kpis(repository: DefectRepository = Depends(get_repository)) -> dict:
    return await repository.get_kpis()


@router.get("/trends")
async def get_trends(repository: DefectRepository = Depends(get_repository)) -> list[dict]:
    return await repository.get_trends(weeks=12)


@router.get("/by_priority")
async def get_by_priority(repository: DefectRepository = Depends(get_repository)) -> list[dict]:
    return await repository.get_by_priority()


@router.get("/by_status")
async def get_by_status(repository: DefectRepository = Depends(get_repository)) -> list[dict]:
    return await repository.get_by_status()