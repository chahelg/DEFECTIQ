from __future__ import annotations

from typing import Any


class NLPService:
    def __init__(self) -> None:
        self._engine = None
        try:
            from app.nlp.intelligence_engine import DefectIntelligenceEngine

            self._engine = DefectIntelligenceEngine()
        except Exception:
            self._engine = None

    async def summarize_defect(self, payload: Any, description: str | None = None) -> dict[str, Any]:
        if self._engine is None:
            return {"summary": description or str(payload), "topics": []}
        if isinstance(payload, str):
            payload = type(
                "LegacyDefectPayload",
                (object,),
                {
                    "title": payload,
                    "short_description": payload,
                    "description": description,
                    "work_notes": None,
                    "close_notes": None,
                    "comments": [],
                    "ticket_id": None,
                    "ticket_number": None,
                },
            )()
        return self._engine.summarize(payload)

    async def find_similar(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return await self.semantic_search(query, top_k=top_k)

    async def semantic_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        if self._engine is None:
            return []
        return self._engine.semantic_search(query, top_k=top_k)

    async def recommend_similar_defects(self, payload: Any, top_k: int = 5) -> list[dict[str, Any]]:
        if self._engine is None:
            return []
        return self._engine.recommend_similar(payload, top_k=top_k)

    async def cluster_defects(self, documents: list[Any], n_clusters: int = 5) -> dict[str, Any]:
        if self._engine is None:
            return {"clusters": [], "labels": []}
        return self._engine.cluster_documents(documents, n_clusters=n_clusters)

    async def topic_model(self, documents: list[Any], top_n_words: int = 5) -> dict[str, Any]:
        if self._engine is None:
            return {"topics": []}
        return self._engine.topic_model(documents, top_n_words=top_n_words)

    async def index_documents(self, documents: list[Any]) -> dict[str, Any]:
        if self._engine is None:
            return {"indexed": 0}
        return self._engine.index_documents(documents)

    async def batch_process(self, documents: list[Any]) -> dict[str, Any]:
        if self._engine is None:
            return {"processed": 0}
        return self._engine.batch_process(documents)
