from __future__ import annotations

from pathlib import Path
from typing import Any

from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self.model_name = settings.EMBEDDING_MODEL
        self._model: Any | None = None

    @property
    def model(self) -> Any:
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
            except Exception:
                self._model = None
        return self._model

    def encode(self, texts: list[str]) -> list[list[float]]:
        if self.model is None:
            return [[0.0] * settings.EMBEDDING_DIMENSION for _ in texts]
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def ensure_directories(self) -> None:
        Path(settings.EMBEDDINGS_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.VECTORDB_DIR).mkdir(parents=True, exist_ok=True)


embedding_service = EmbeddingService()
