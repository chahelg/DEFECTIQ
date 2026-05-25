"""Defect clustering engine."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import select

from app.models import Defect
from app.nlp.embeddings_service import EmbeddingsService
from app.nlp.text_processing_service import TextProcessingService


class ClusteringService:
    @classmethod
    async def cluster_defects(cls, defects: list[dict[str, Any]], db=None) -> dict[str, Any]:
        if not defects:
            return {"clusters": [], "status": "empty"}

        documents = TextProcessingService.prepare_documents(defects)
        try:
            from sklearn.cluster import KMeans
            from sklearn.feature_extraction.text import TfidfVectorizer
        except ImportError:
            clusters = {"cluster_0": defects}
            return {"clusters": [{"cluster_id": key, "size": len(value)} for key, value in clusters.items()], "status": "fallback"}

        vectorizer = TfidfVectorizer(stop_words="english", max_features=2000)
        matrix = vectorizer.fit_transform(documents)
        cluster_count = max(2, min(8, len(defects) // 5 or 2))
        labels = KMeans(n_clusters=cluster_count, random_state=42, n_init=10).fit_predict(matrix)

        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for defect, label in zip(defects, labels, strict=False):
            cluster_id = f"cluster_{int(label)}"
            grouped[cluster_id].append(defect)
            defect["cluster_id"] = cluster_id

        if db is not None:
            result = await db.execute(select(Defect).where(Defect.id.in_([defect["id"] for defect in defects])))
            for record in result.scalars().all():
                matching = next((item for item in defects if str(item["id"]) == str(record.id)), None)
                if matching is not None:
                    record.cluster_id = matching.get("cluster_id")

        summary = [
            {"cluster_id": cluster_id, "size": len(items), "sample_titles": [item.get("title") for item in items[:3]]}
            for cluster_id, items in grouped.items()
        ]
        return {"clusters": summary, "status": "clustered"}

    @classmethod
    async def get_cluster_overview(cls, defects: list[dict[str, Any]]) -> dict[str, Any]:
        grouped: dict[str, int] = defaultdict(int)
        for defect in defects:
            grouped[str(defect.get("cluster_id") or "unassigned")] += 1
        return {"clusters": [{"cluster_id": key, "size": value} for key, value in grouped.items()]}
