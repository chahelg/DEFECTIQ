"""Conversational assistant for defect analytics."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select

from app.core.config import settings
from app.models import ChatHistory, Defect
from app.nlp.embeddings_service import EmbeddingsService
from app.nlp.keyword_service import KeywordService


class ChatService:
    @staticmethod
    def _intent(message: str) -> str:
        normalized = message.lower()
        if any(token in normalized for token in ["predict", "forecast", "estimate"]):
            return "prediction"
        if any(token in normalized for token in ["cluster", "group", "topic"]):
            return "nlp"
        if any(token in normalized for token in ["insight", "summary", "executive"]):
            return "insights"
        return "general"

    @classmethod
    async def handle_message(cls, message: str, db, conversation_id: str | None = None, user_id: str | None = None) -> dict[str, Any]:
        conversation_uuid = uuid.UUID(conversation_id) if conversation_id else uuid.uuid4()
        intent = cls._intent(message)
        defects_result = await db.execute(select(Defect).order_by(Defect.created_at.desc()).limit(5))
        recent_defects = defects_result.scalars().all()
        semantic_results = await EmbeddingsService.search_similar(message, top_k=3)

        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI

                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                completion = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a concise defect operations assistant."},
                        {"role": "user", "content": f"User message: {message}\nIntent: {intent}\nRecent defects: {[defect.title for defect in recent_defects]}\nSemantic matches: {semantic_results}"},
                    ],
                )
                reply = completion.choices[0].message.content or "I could not produce a response."
            except Exception:
                reply = cls._fallback_reply(message, semantic_results, recent_defects)
        else:
            reply = cls._fallback_reply(message, semantic_results, recent_defects)

        db.add(
            ChatHistory(
                conversation_id=conversation_uuid,
                user_id=uuid.UUID(user_id) if user_id else None,
                role="user",
                content=message,
                intent=intent,
                metadata_json={"timestamp": datetime.now(UTC).isoformat()},
            )
        )
        db.add(
            ChatHistory(
                conversation_id=conversation_uuid,
                user_id=uuid.UUID(user_id) if user_id else None,
                role="assistant",
                content=reply,
                intent=intent,
                metadata_json={"sources": [item.get("id") for item in semantic_results[:3]]},
            )
        )

        return {
            "conversation_id": str(conversation_uuid),
            "intent": intent,
            "reply": reply,
            "semantic_matches": semantic_results,
        }

    @staticmethod
    def _fallback_reply(message: str, semantic_results: list[dict[str, Any]], recent_defects: list[Defect]) -> str:
        keywords = KeywordService.classify_topic(message)
        if semantic_results:
            top_match = semantic_results[0]
            return f"I found a related defect: {top_match.get('title')} ({top_match.get('status')}). Topic: {keywords}."
        if recent_defects:
            return f"I do not have a direct match, but the latest defect is '{recent_defects[0].title}'. Topic: {keywords}."
        return f"I could not find related defects yet. Topic: {keywords}."
