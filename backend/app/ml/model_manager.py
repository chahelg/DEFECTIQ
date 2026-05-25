"""High-level orchestration for model training and status checks."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select

from app.models import Defect



class ModelManager:
    @staticmethod
    async def train_all(db) -> dict[str, Any]:
        from app.ml.assignment_recommender import AssignmentRecommender
        from app.ml.resolution_predictor import ResolutionPredictor
        from app.ml.sla_predictor import SLAPredictor
        from app.nlp.embeddings_service import EmbeddingsService

        result = await db.execute(select(Defect))
        defects = [
            {
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
            for defect in result.scalars().all()
        ]
        sla = await SLAPredictor.train(defects)
        resolution = await ResolutionPredictor.train(defects)
        assignment = await AssignmentRecommender.train(defects)
        try:
            await EmbeddingsService.build_index([
                {"id": defect["id"], "text": f"{defect.get('title') or ''} {defect.get('description') or ''}".strip()}
                for defect in defects
            ])
        except Exception:
            pass
        return {"sla": sla, "resolution": resolution, "assignment": assignment, "status": "completed"}

    @staticmethod
    async def get_all_model_status() -> dict[str, Any]:
        from app.ml.assignment_recommender import AssignmentRecommender
        from app.ml.resolution_predictor import ResolutionPredictor
        from app.ml.sla_predictor import SLAPredictor
        from app.nlp.embeddings_service import EmbeddingsService

        return {
            "sla": await SLAPredictor.get_model_info(),
            "resolution": await ResolutionPredictor.get_model_info(),
            "assignment": {
                **({"status": "trained"} if AssignmentRecommender.MODEL_PATH.exists() else {"status": "not_trained"}),
                "exists": AssignmentRecommender.MODEL_PATH.exists(),
            },
            "embeddings_index": await EmbeddingsService.get_index_stats(),
        }
