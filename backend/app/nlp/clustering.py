"""Defect clustering utilities."""

from __future__ import annotations

from typing import Any

from app.services.nlp_service import NLPService


class DefectClusterer:
    def __init__(self, n_clusters: int = 8) -> None:
        self.n_clusters = n_clusters
        self.service = NLPService()

    async def cluster(self, documents: list[Any]) -> dict[str, Any]:
        return await self.service.cluster_defects(documents, n_clusters=self.n_clusters)
