"""AI insights generation for dashboard and analytics use cases."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select

from app.core.config import settings
from app.models import AiSummary, Defect
from app.nlp.summarizer_service import SummarizerService


class InsightsService:
    @staticmethod
    async def get_metrics(db) -> dict[str, Any]:
        total_result = await db.execute(select(func.count(Defect.id)))
        breached_result = await db.execute(select(func.count(Defect.id)).where(Defect.is_sla_breached.is_(True)))
        duration_rows = await db.execute(select(Defect.opened_at, Defect.resolved_at).where(Defect.resolved_at.is_not(None), Defect.opened_at.is_not(None)))
        total = total_result.scalar_one()
        breached = breached_result.scalar_one()
        durations: list[float] = []
        for opened_at, resolved_at in duration_rows:
            if opened_at is None or resolved_at is None:
                continue
            durations.append(max((resolved_at - opened_at).total_seconds() / 3600.0, 0.0))

        avg_resolution = sum(durations) / len(durations) if durations else 0.0
        return {
            "total_defects": int(total or 0),
            "sla_breaches": int(breached or 0),
            "average_resolution_hours": round(float(avg_resolution), 2),
        }

    @classmethod
    async def generate_insights(cls, db) -> dict[str, Any]:
        metrics = await cls.get_metrics(db)
        defect_rows = await db.execute(select(Defect).order_by(Defect.created_at.desc()).limit(20))
        defects = [
            {
                "id": str(defect.id),
                "title": defect.title,
                "description": defect.description,
                "priority": defect.priority,
                "status": defect.status,
            }
            for defect in defect_rows.scalars().all()
        ]
        summary = await SummarizerService.summarize_text(" ".join(item["title"] for item in defects))
        result = {
            "metrics": metrics,
            "summary": summary,
            "recommendations": ["Focus on high-priority unresolved defects", "Review SLA-breached items daily"],
            "method": "fallback",
        }
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                completion = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an operations analyst for defect management."},
                        {"role": "user", "content": f"Create concise executive insights from these metrics and sample defects: {result}"},
                    ],
                    response_format={"type": "json_object"},
                )
                result = {"openai": completion.choices[0].message.content, "metrics": metrics, "method": "openai"}
            except Exception:
                pass

        existing = await db.execute(select(AiSummary).where(AiSummary.summary_type == "insights"))
        row = existing.scalars().first()
        if row is None:
            db.add(AiSummary(summary_type="insights", content=result, method=result.get("method")))
        else:
            row.content = result
            row.method = result.get("method")
        return result
