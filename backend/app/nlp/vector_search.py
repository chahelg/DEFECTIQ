"""FAISS-based vector search engine."""

from __future__ import annotations

from typing import Any

from app.services.vector_search_service import VectorSearchService


class VectorSearchEngine:
    def __init__(self) -> None:
        self.service = VectorSearchService()

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        return self.service.search(query, top_k=top_k)

    def index_documents(self, documents: list[Any]) -> dict[str, Any]:
        return self.service.index_documents(documents)
