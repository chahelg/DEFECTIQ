from __future__ import annotations

from app.core.config import settings


class TextEmbeddingEngine:
    def __init__(self) -> None:
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            except Exception:
                self._model = None
        return self._model

    def encode(self, texts: list[str]) -> list[list[float]]:
        if self.model is None:
            return [[0.0] * settings.EMBEDDING_DIMENSION for _ in texts]
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
