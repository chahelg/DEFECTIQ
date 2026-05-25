"""FAISS vector search service."""

from __future__ import annotations

from typing import Any

from app.nlp.intelligence_engine import DefectIntelligenceEngine


class VectorSearchService:
    def __init__(self, engine: DefectIntelligenceEngine | None = None) -> None:
        self.engine = engine or DefectIntelligenceEngine()

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return self.engine.semantic_search(query, top_k=top_k)

    def index_documents(self, documents: list[Any]) -> dict[str, Any]:
        return self.engine.index_documents(documents)