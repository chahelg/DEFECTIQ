"""Phase 2 insights endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from app.api.dependencies import current_user_id, db_session
from app.services.insights_service import InsightsService

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("/metrics")
async def metrics(session=Depends(db_session), _: str = Depends(current_user_id)) -> dict[str, Any]:
    return await InsightsService.get_metrics(session)


@router.post("/generate")
async def generate(session=Depends(db_session), _: str = Depends(current_user_id)) -> dict[str, Any]:
    return await InsightsService.generate_insights(session)


@router.get("/latest")
async def latest(session=Depends(db_session), _: str = Depends(current_user_id)) -> dict[str, Any]:
    return await InsightsService.generate_insights(session)
