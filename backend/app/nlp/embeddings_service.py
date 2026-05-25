"""Semantic embeddings and FAISS index management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import settings
from app.core.paths import get_ml_models_dir
from app.nlp.text_processing_service import TextProcessingService


class EmbeddingsService:
    INDEX_PATH = get_ml_models_dir() / "faiss.index"
    METADATA_PATH = get_ml_models_dir() / "faiss_metadata.joblib"
    _index = None
    _metadata: list[dict[str, Any]] = []
    _model = None

    @classmethod
    def _load_model(cls):
        if cls._model is not None:
            return cls._model
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            return None
        cls._model = SentenceTransformer(settings.EMBEDDINGS_MODEL)
        return cls._model

    @classmethod
    def _load_faiss(cls):
        if cls._index is not None:
            return cls._index
        if not cls.INDEX_PATH.exists():
            return None
        try:
            import faiss
        except ImportError:
            return None
        import joblib

        cls._index = faiss.read_index(str(cls.INDEX_PATH))
        if cls.METADATA_PATH.exists():
            cls._metadata = joblib.load(cls.METADATA_PATH)
        return cls._index

    @classmethod
    async def build_index(cls, defects: list[dict[str, Any]]) -> dict[str, Any]:
        import joblib

        model = cls._load_model()
        if model is None:
            cls._metadata = defects
            joblib.dump(defects, cls.METADATA_PATH)
            return {"status": "embeddings_unavailable", "indexed": len(defects)}

        documents = TextProcessingService.prepare_documents(defects)
        if not documents:
            return {"status": "no_documents", "indexed": 0}

        embeddings = model.encode(documents, convert_to_numpy=True, normalize_embeddings=True)
        try:
            import faiss
        except ImportError:
            cls._metadata = defects
            joblib.dump(defects, cls.METADATA_PATH)
            return {"status": "faiss_missing", "indexed": len(defects)}

        import numpy as np

        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(np.asarray(embeddings, dtype="float32"))
        cls._index = index
        cls._metadata = defects
        faiss.write_index(index, str(cls.INDEX_PATH))
        joblib.dump(defects, cls.METADATA_PATH)
        return {"status": "indexed", "indexed": len(defects), "dimension": int(embeddings.shape[1])}

    @classmethod
    async def search_similar(cls, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        import numpy as np  # noqa: F401

        model = cls._load_model()
        index = cls._load_faiss()
        if model is None or index is None or not cls._metadata:
            normalized = TextProcessingService.normalize_text(query)
            return [item for item in cls._metadata[:top_k] if normalized and normalized[:5] in TextProcessingService.normalize_text(f"{item.get('title')} {item.get('description')}")]

        import faiss
        import numpy as np

        vector = model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        scores, indices = index.search(vector, top_k)
        results: list[dict[str, Any]] = []
        for score, index_position in zip(scores[0], indices[0], strict=False):
            if index_position < 0 or index_position >= len(cls._metadata):
                continue
            item = dict(cls._metadata[index_position])
            item["score"] = float(score)
            results.append(item)
        return results

    @classmethod
    async def get_index_stats(cls) -> dict[str, Any]:
        index = cls._load_faiss()
        return {
            "exists": index is not None,
            "count": int(index.ntotal) if index is not None else len(cls._metadata),
            "path": str(cls.INDEX_PATH),
        }
