"""KPI ontology snapshot endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.manager_decision_service import ManagerDecisionService

router = APIRouter(prefix="/kpi-ontology", tags=["KPI Ontology"])


async def get_service(session: AsyncSession = Depends(get_db)) -> ManagerDecisionService:
    return ManagerDecisionService(session)


@router.get("/snapshot")
async def get_kpi_snapshot(service: ManagerDecisionService = Depends(get_service)) -> dict:
    return await service.get_kpi_ontology_snapshot()
