"""Workflow Intelligence endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.workflow_intelligence_service import WorkflowIntelligenceService

router = APIRouter(prefix="/workflow-intelligence", tags=["Workflow Intelligence"])


async def get_service(session: AsyncSession = Depends(get_db)) -> WorkflowIntelligenceService:
    return WorkflowIntelligenceService(session)


@router.get("/snapshot")
async def get_workflow_snapshot(service: WorkflowIntelligenceService = Depends(get_service)) -> dict:
    return await service.get_snapshot()
