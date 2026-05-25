"""Manager Decision Center endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.manager_decision_service import ManagerDecisionService

router = APIRouter(prefix="/manager-decision", tags=["Manager Decision"])


async def get_service(session: AsyncSession = Depends(get_db)) -> ManagerDecisionService:
    return ManagerDecisionService(session)


@router.get("/command-center")
async def get_command_center(service: ManagerDecisionService = Depends(get_service)) -> dict:
    return await service.get_command_center_snapshot()
