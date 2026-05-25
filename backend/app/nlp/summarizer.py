"""Defect summarizer wrapper."""

from __future__ import annotations

from typing import Any

from app.services.nlp_service import NLPService


class DefectSummarizer:
    def __init__(self) -> None:
        self.service = NLPService()

    async def summarize(self, payload: Any, description: str | None = None) -> dict[str, Any]:
        return await self.service.summarize_defect(payload, description)
