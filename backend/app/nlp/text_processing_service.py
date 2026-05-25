"""Shared text cleaning helpers for NLP services."""

from __future__ import annotations

import re
from typing import Any


class TextProcessingService:
    @staticmethod
    def normalize_text(text: str | None) -> str:
        value = (text or "").lower().strip()
        value = re.sub(r"[^a-z0-9\s]", " ", value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    @staticmethod
    def split_sentences(text: str | None) -> list[str]:
        if not text:
            return []
        return [sentence.strip() for sentence in re.split(r"[.!?]+", text) if sentence.strip()]

    @staticmethod
    def prepare_documents(defects: list[dict[str, Any]]) -> list[str]:
        return [
            TextProcessingService.normalize_text(f"{defect.get('title') or ''} {defect.get('description') or ''}")
            for defect in defects
        ]
