"""SLA Risk Intelligence endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.sla_risk_service import SLARiskService

router = APIRouter(prefix="/sla-risk", tags=["SLA Risk"])


async def get_service(session: AsyncSession = Depends(get_db)) -> SLARiskService:
    return SLARiskService(session)


@router.get("/snapshot")
async def get_sla_risk_snapshot(service: SLARiskService = Depends(get_service)) -> dict:
    return await service.get_risk_snapshot()
