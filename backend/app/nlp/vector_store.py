from __future__ import annotations

import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from app.core.config import settings


@dataclass(slots=True)
class VectorStoreDocument:
    ticket_id: str | None
    ticket_number: str | None
    title: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


class FAISSVectorStore:
    def __init__(self, dimension: int | None = None) -> None:
        self.dimension = dimension or settings.EMBEDDING_DIMENSION
        self.index_path = Path(settings.FAISS_INDEX_PATH)
        self.metadata_path = Path(settings.FAISS_METADATA_PATH)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        self._index = None
        self._documents: list[VectorStoreDocument] = []

    def _faiss(self):
        try:
            import faiss

            return faiss
        except Exception:
            return None

    @property
    def index(self):
        faiss = self._faiss()
        if faiss is None:
            return None
        if self._index is None:
            if self.index_path.exists():
                self._index = faiss.read_index(str(self.index_path))
            else:
                self._index = faiss.IndexFlatIP(self.dimension)
        return self._index

    @property
    def documents(self) -> list[VectorStoreDocument]:
        if not self._documents and self.metadata_path.exists():
            with self.metadata_path.open("rb") as metadata_file:
                raw_documents = pickle.load(metadata_file)
            self._documents = [
                VectorStoreDocument(
                    ticket_id=item.get("ticket_id"),
                    ticket_number=item.get("ticket_number"),
                    title=item.get("title", ""),
                    text=item.get("text", ""),
                    metadata=item.get("metadata", {}),
                )
                for item in raw_documents
            ]
        return self._documents

    def save(self) -> None:
        faiss = self._faiss()
        if faiss is None or self._index is None:
            return
        faiss.write_index(self._index, str(self.index_path))
        serializable_documents = [
            {
                "ticket_id": document.ticket_id,
                "ticket_number": document.ticket_number,
                "title": document.title,
                "text": document.text,
                "metadata": document.metadata,
            }
            for document in self._documents
        ]
        with self.metadata_path.open("wb") as metadata_file:
            pickle.dump(serializable_documents, metadata_file)

    def reset(self) -> None:
        faiss = self._faiss()
        if faiss is None:
            self._index = None
            self._documents = []
            return
        self._index = faiss.IndexFlatIP(self.dimension)
        self._documents = []
        self.save()

    def set_documents(self, documents: list[VectorStoreDocument], embeddings: np.ndarray) -> None:
        faiss = self._faiss()
        if faiss is None:
            self._documents = documents
            return
        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D array")
        if embeddings.shape[0] != len(documents):
            raise ValueError("Document and embedding counts must match")
        self._documents = documents
        self._index = faiss.IndexFlatIP(embeddings.shape[1])
        self._index.add(embeddings.astype("float32"))
        self.save()

    def add_embeddings(self, documents: list[VectorStoreDocument], embeddings: np.ndarray) -> None:
        faiss = self._faiss()
        if faiss is None:
            self._documents.extend(documents)
            return
        if self.index is None or self._index.ntotal == 0:
            self.set_documents(documents, embeddings)
            return
        if embeddings.shape[1] != self._index.d:
            raise ValueError("Embedding dimension mismatch")
        self._index.add(embeddings.astype("float32"))
        self._documents.extend(documents)
        self.save()

    def search(self, embeddings: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        faiss = self._faiss()
        if faiss is None or self.index is None or getattr(self._index, "ntotal", 0) == 0:
            empty_scores = np.empty((1, 0), dtype="float32")
            empty_indices = np.empty((1, 0), dtype="int64")
            return empty_scores, empty_indices
        return self._index.search(embeddings.astype("float32"), top_k)
