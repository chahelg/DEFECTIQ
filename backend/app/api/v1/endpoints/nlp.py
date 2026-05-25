"""Phase 2 NLP endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import current_user_id, db_session
from app.ml.model_manager import ModelManager
from app.models import Defect
from app.nlp.clustering_service import ClusteringService
from app.nlp.embeddings_service import EmbeddingsService
from app.nlp.keyword_service import KeywordService
from app.nlp.summarizer_service import SummarizerService

router = APIRouter(prefix="/nlp", tags=["NLP"])


class SummarizeRequest(BaseModel):
    defect_id: str | None = None
    title: str = ""
    description: str = ""


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class ClusterRequest(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000)


def _defect_payload(defect: Defect) -> dict[str, Any]:
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
        "cluster_id": defect.cluster_id,
    }


@router.post("/summarize")
async def summarize(payload: SummarizeRequest, session: AsyncSession = Depends(db_session), _: str = Depends(current_user_id)) -> dict[str, Any]:
    if payload.defect_id:
        result = await session.execute(select(Defect).where(Defect.id == payload.defect_id))
        defect = result.scalars().first()
        if defect is None:
            raise HTTPException(status_code=404, detail="Defect not found")
        return await SummarizerService.summarize_defect(_defect_payload(defect), db=session)
    return await SummarizerService.summarize_text(f"{payload.title} {payload.description}")


@router.post("/semantic-search")
async def semantic_search(payload: SearchRequest, _: str = Depends(current_user_id)) -> dict[str, Any]:
    results = await EmbeddingsService.search_similar(payload.query, top_k=payload.top_k)
    return {"query": payload.query, "top_k": payload.top_k, "results": results}


@router.get("/keywords")
async def keywords(session: AsyncSession = Depends(db_session), _: str = Depends(current_user_id)) -> dict[str, Any]:
    result = await session.execute(select(Defect.title, Defect.description))
    texts = [f"{title or ''} {description or ''}" for title, description in result.all()]
    return {"keywords": KeywordService.extract_keywords(texts)}


@router.post("/cluster")
async def cluster(payload: ClusterRequest, session: AsyncSession = Depends(db_session), _: str = Depends(current_user_id)) -> dict[str, Any]:
    result = await session.execute(select(Defect).order_by(Defect.created_at.desc()).limit(payload.limit))
    defects = [_defect_payload(defect) for defect in result.scalars().all()]
    return await ClusteringService.cluster_defects(defects, db=session)


@router.get("/status")
async def status(_: str = Depends(current_user_id)) -> dict[str, Any]:
    return await ModelManager.get_all_model_status()