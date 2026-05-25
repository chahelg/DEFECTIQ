from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services.analytics_service import backlog_by_assignment_group, defects_older_than, trends_by_week
from app.services.snapshot_service import get_snapshot, refresh_snapshots
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

router = APIRouter()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get('/analytics/backlog')
async def api_backlog(db: AsyncSession = Depends(get_db)):
    snap = await get_snapshot(db, 'backlog_snapshot')
    if snap is not None:
        return snap
    return await backlog_by_assignment_group(db)


@router.get('/analytics/older_than/{days}')
async def api_older(days: int, db: AsyncSession = Depends(get_db)):
    return await defects_older_than(db, days)


@router.get('/analytics/trends')
async def api_trends(db: AsyncSession = Depends(get_db)):
    snap = await get_snapshot(db, 'trends_snapshot')
    if snap is not None:
        return snap
    return await trends_by_week(db)


@router.post('/analytics/refresh_snapshots')
async def api_refresh(db: AsyncSession = Depends(get_db)):
    await refresh_snapshots(db)
    return {'status':'ok'}
"""Analytics endpoints."""

from fastapi import APIRouter, Depends

from app.api.dependencies import db_session
from app.repositories.defect_repository import DefectRepository
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service(session=Depends(db_session)) -> AnalyticsService:
    return AnalyticsService(DefectRepository(session))


@router.get("/status")
async def by_status(service: AnalyticsService = Depends(get_analytics_service)) -> dict[str, int]:
    return await service.by_status()


@router.get("/priority")
async def by_priority(service: AnalyticsService = Depends(get_analytics_service)) -> dict[str, int]:
    return await service.by_priority()


@router.get("/assignment-groups")
async def by_assignment_group(service: AnalyticsService = Depends(get_analytics_service)) -> dict[str, int]:
    return await service.by_assignment_group()