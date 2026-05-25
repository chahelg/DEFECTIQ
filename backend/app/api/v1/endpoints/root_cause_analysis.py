"""Root Cause Analysis endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.root_cause_analysis_service import RootCauseAnalysisService

router = APIRouter(prefix="/root-cause-analysis", tags=["Root Cause Analysis"])


async def get_service(session: AsyncSession = Depends(get_db)) -> RootCauseAnalysisService:
    return RootCauseAnalysisService(session)


@router.get("/snapshot")
async def get_rca_snapshot(service: RootCauseAnalysisService = Depends(get_service)) -> dict:
    return await service.get_snapshot()
