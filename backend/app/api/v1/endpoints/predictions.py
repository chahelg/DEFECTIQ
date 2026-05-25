"""Phase 2 prediction endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import current_user_id, db_session
from app.ml.assignment_recommender import AssignmentRecommender
from app.ml.model_manager import ModelManager
from app.ml.resolution_predictor import ResolutionPredictor
from app.ml.sla_predictor import SLAPredictor
from app.models import Defect

router = APIRouter(prefix="/predictions", tags=["Predictions"])


def _payload(defect: Defect) -> dict[str, Any]:
    return {
        "id": str(defect.id),
        "number": defect.number,
        "title": defect.title,
        "description": defect.description,
        "priority": defect.priority,
        "status": defect.status,
        "category": defect.category,
        "assigned_to": defect.assigned_to,
        "opened_at": defect.opened_at,
        "resolved_at": defect.resolved_at,
        "reopen_count": defect.reopen_count,
        "is_sla_breached": defect.is_sla_breached,
    }


async def _get_defect(session: AsyncSession, defect_id: str) -> Defect:
    result = await session.execute(select(Defect).where(Defect.id == defect_id))
    defect = result.scalars().first()
    if defect is None:
        raise HTTPException(status_code=404, detail="Defect not found")
    return defect


@router.get("/status")
async def status(_: str = Depends(current_user_id)) -> dict[str, Any]:
    return await ModelManager.get_all_model_status()


@router.post("/train")
async def train(session: AsyncSession = Depends(db_session), _: str = Depends(current_user_id)) -> dict[str, Any]:
    return await ModelManager.train_all(session)


@router.get("/{defect_id}/sla")
async def predict_sla(defect_id: str, session: AsyncSession = Depends(db_session), _: str = Depends(current_user_id)) -> dict[str, Any]:
    defect = await _get_defect(session, defect_id)
    return await SLAPredictor.predict(_payload(defect))


@router.get("/{defect_id}/resolution-time")
async def predict_resolution(defect_id: str, session: AsyncSession = Depends(db_session), _: str = Depends(current_user_id)) -> dict[str, Any]:
    defect = await _get_defect(session, defect_id)
    return await ResolutionPredictor.predict(_payload(defect))


@router.get("/{defect_id}/assignment")
async def recommend_assignment(defect_id: str, session: AsyncSession = Depends(db_session), _: str = Depends(current_user_id)) -> dict[str, Any]:
    defect = await _get_defect(session, defect_id)
    return await AssignmentRecommender.recommend(_payload(defect), db=session)
