"""GenAI-backed summarization with deterministic fallback."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select

from app.core.config import settings
from app.models import AiSummary, Defect
from app.nlp.text_processing_service import TextProcessingService


class SummarizerService:
    @staticmethod
    def _fallback_summary(defect: dict[str, Any]) -> dict[str, Any]:
        title = defect.get("title") or "Unknown defect"
        description = defect.get("description") or "No description available"
        return {
            "summary": f"{title}: {description[:240]}",
            "actions": ["triage", "assign", "confirm severity"],
            "risk": defect.get("priority") or "medium",
            "method": "fallback",
        }

    @classmethod
    async def summarize_defect(cls, defect: dict[str, Any], db=None) -> dict[str, Any]:
        prompt = f"Summarize this defect in JSON with summary, actions, risk, root_cause, and recommended_next_step: {defect}"
        response_text = None
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                completion = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You summarize defect tickets as compact JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                )
                response_text = completion.choices[0].message.content
            except Exception:
                response_text = None

        summary = cls._fallback_summary(defect)
        if response_text:
            try:
                summary = json.loads(response_text)
                summary["method"] = "openai"
            except Exception:
                summary = cls._fallback_summary(defect)

        if db is not None:
            existing = await db.execute(select(AiSummary).where(AiSummary.defect_id == defect.get("id"), AiSummary.summary_type == "defect"))
            row = existing.scalars().first()
            if row is None:
                db.add(AiSummary(defect_id=defect.get("id"), summary_type="defect", content=summary, method=summary.get("method")))
            else:
                row.content = summary
                row.method = summary.get("method")
        return summary

    @classmethod
    async def summarize_batch(cls, defects: list[dict[str, Any]], db=None) -> dict[str, Any]:
        summaries = [await cls.summarize_defect(defect, db=db) for defect in defects]
        return {"summaries": summaries, "count": len(summaries)}

    @classmethod
    async def summarize_text(cls, text: str) -> dict[str, Any]:
        sentences = TextProcessingService.split_sentences(text)
        if not sentences:
            return {"summary": "No content available.", "method": "fallback"}
        return {"summary": " ".join(sentences[:2]), "method": "fallback"}
