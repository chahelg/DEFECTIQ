"""Workload Intelligence endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.workload_intelligence_service import WorkloadIntelligenceService

router = APIRouter(prefix="/workload-intelligence", tags=["Workload Intelligence"])


async def get_service(session: AsyncSession = Depends(get_db)) -> WorkloadIntelligenceService:
    return WorkloadIntelligenceService(session)


@router.get("/snapshot")
async def get_workload_snapshot(service: WorkloadIntelligenceService = Depends(get_service)) -> dict:
    return await service.get_snapshot()
