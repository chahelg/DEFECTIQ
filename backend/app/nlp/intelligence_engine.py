"""DefectIQ NLP intelligence engine."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from app.core.config import settings
from app.nlp.keyword_extractor import KeywordExtractor
from app.nlp.text_processor import TextProcessor
from app.nlp.vector_store import FAISSVectorStore, VectorStoreDocument
from app.services.embedding_service import EmbeddingService

try:  # pragma: no cover - optional dependency is present in production requirements
    from bertopic import BERTopic
except Exception:  # pragma: no cover
    BERTopic = None

try:  # pragma: no cover - optional summarization model
    from transformers import pipeline
except Exception:  # pragma: no cover
    pipeline = None


@dataclass(slots=True)
class DefectTextBundle:
    ticket_id: str | None
    ticket_number: str | None
    title: str
    source_text: str
    short_description: str
    description: str
    work_notes: str
    close_notes: str
    comments: list[str]
    metadata: dict[str, Any]


def _compact(value: str | None) -> str:
    if not value:
        return ""
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned


def _sentences(text: str) -> list[str]:
    return [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", text) if segment.strip()]


def _safe_join(values: list[str]) -> str:
    return " ".join(segment for segment in values if segment).strip()


@lru_cache(maxsize=1)
def _load_summarizer():
    if pipeline is None:
        return None

    return pipeline(
        task="summarization",
        model="sshleifer/distilbart-cnn-12-6",
        device=-1,
    )


class DefectIntelligenceEngine:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or EmbeddingService()
        self.text_processor = TextProcessor()
        self.keyword_extractor = KeywordExtractor()
        self.vector_store = FAISSVectorStore(settings.EMBEDDING_DIMENSION)
        self._summarizer = None
        self._topic_model = None
        Path(settings.MODEL_DIR).mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------------
    # Preprocessing
    # ---------------------------------------------------------------------
    def build_text_bundle(self, payload: Any) -> DefectTextBundle:
        short_description = _compact(
            getattr(payload, "short_description", None)
            or getattr(payload, "title", None)
            or getattr(payload, "ticket_number", None)
            or getattr(payload, "ticket_id", None)
        )
        description = _compact(getattr(payload, "description", None))
        work_notes = _compact(getattr(payload, "work_notes", None))
        close_notes = _compact(getattr(payload, "close_notes", None))
        comments_raw = getattr(payload, "comments", None) or []
        comments = [_compact(comment) for comment in comments_raw if _compact(comment)]
        title = _compact(getattr(payload, "title", None) or short_description)

        source_text = _safe_join([short_description, description, work_notes, close_notes, _safe_join(comments)])
        metadata = {
            "ticket_id": getattr(payload, "ticket_id", None),
            "ticket_number": getattr(payload, "ticket_number", None),
        }

        return DefectTextBundle(
            ticket_id=metadata["ticket_id"],
            ticket_number=metadata["ticket_number"],
            title=title or "Untitled defect",
            source_text=source_text,
            short_description=short_description,
            description=description,
            work_notes=work_notes,
            close_notes=close_notes,
            comments=comments,
            metadata=metadata,
        )

    def preprocess_text(self, text: str) -> str:
        text = _compact(text)
        text = text.replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        text = re.sub(r"\bINC\d+\b", " incident ", text, flags=re.IGNORECASE)
        text = re.sub(r"[^\w\s\-./]", " ", text)
        text = re.sub(r"\s+", " ", text).strip().lower()
        return text

    def preprocess_documents(self, documents: list[Any]) -> list[DefectTextBundle]:
        return [self.build_text_bundle(document) for document in documents]

    def compose_document(self, bundle: DefectTextBundle) -> str:
        return self.preprocess_text(
            _safe_join(
                [
                    bundle.short_description,
                    bundle.description,
                    bundle.work_notes,
                    bundle.close_notes,
                    _safe_join(bundle.comments),
                ]
            )
        )

    # ---------------------------------------------------------------------
    # Embeddings
    # ---------------------------------------------------------------------
    def embed_texts(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, settings.EMBEDDING_DIMENSION), dtype="float32")

        embeddings = np.array(self.embedding_service.encode(texts), dtype="float32")
        return embeddings

    def embed_documents(self, documents: list[DefectTextBundle]) -> np.ndarray:
        return self.embed_texts([self.compose_document(document) for document in documents])

    # ---------------------------------------------------------------------
    # Vector storage / semantic search
    # ---------------------------------------------------------------------
    def index_documents(self, documents: list[Any]) -> dict[str, Any]:
        bundles = self.preprocess_documents(documents)
        embeddings = self.embed_documents(bundles)
        if not bundles:
            self.vector_store.reset()
            return {
                "indexed_documents": 0,
                "vector_count": 0,
                "faiss_index_path": str(self.vector_store.index_path),
                "metadata_path": str(self.vector_store.metadata_path),
            }

        store_documents = [
            VectorStoreDocument(
                ticket_id=bundle.ticket_id,
                ticket_number=bundle.ticket_number,
                title=bundle.title,
                text=self.compose_document(bundle),
                metadata={**bundle.metadata, "source_text": bundle.source_text},
            )
            for bundle in bundles
        ]
        self.vector_store.set_documents(store_documents, embeddings)
        return {
            "indexed_documents": len(store_documents),
            "vector_count": int(self.vector_store.index.ntotal),
            "faiss_index_path": str(self.vector_store.index_path),
            "metadata_path": str(self.vector_store.metadata_path),
        }

    def semantic_search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        normalized_query = self.preprocess_text(query)
        if not normalized_query or self.vector_store.index.ntotal == 0:
            return []

        query_embedding = self.embed_texts([normalized_query])
        scores, indices = self.vector_store.search(query_embedding, top_k)
        results: list[dict[str, Any]] = []
        documents = self.vector_store.documents

        for score, index in zip(scores[0], indices[0], strict=False):
            if index < 0 or index >= len(documents):
                continue
            document = documents[index]
            results.append(
                {
                    "ticket_id": document.ticket_id,
                    "ticket_number": document.ticket_number,
                    "title": document.title,
                    "score": float(score),
                    "snippet": document.text[:240],
                    "metadata": document.metadata,
                }
            )
        return results

    def recommend_similar(self, payload: Any, top_k: int = 5) -> list[dict[str, Any]]:
        bundle = self.build_text_bundle(payload)
        if self.vector_store.index.ntotal == 0:
            return []

        query_embedding = self.embed_texts([self.compose_document(bundle)])
        scores, indices = self.vector_store.search(query_embedding, top_k)
        recommendations: list[dict[str, Any]] = []
        documents = self.vector_store.documents

        for score, index in zip(scores[0], indices[0], strict=False):
            if index < 0 or index >= len(documents):
                continue
            document = documents[index]
            recommendations.append(
                {
                    "ticket_id": document.ticket_id,
                    "ticket_number": document.ticket_number,
                    "title": document.title,
                    "similarity_score": float(score),
                    "snippet": document.text[:240],
                    "metadata": document.metadata,
                }
            )
        return recommendations

    # ---------------------------------------------------------------------
    # Summarization / extraction
    # ---------------------------------------------------------------------
    def _summarizer_pipeline(self):
        if self._summarizer is None:
            self._summarizer = _load_summarizer()
        return self._summarizer

    def summarize(self, payload: Any) -> dict[str, Any]:
        bundle = self.build_text_bundle(payload)
        combined_text = bundle.source_text or bundle.title
        normalized = self.preprocess_text(combined_text)
        keywords = self.keyword_extractor.extract(normalized)

        root_cause = self.extract_root_cause(bundle)
        resolution = self.extract_resolution(bundle)
        action_taken = self.extract_action_taken(bundle)
        category = self.classify_category(bundle, keywords)
        confidence = self.estimate_confidence(bundle, keywords)

        summary_text = self._summarize_with_huggingface(combined_text)
        if summary_text:
            root_cause = summary_text.get("root_cause_summary", root_cause)
            resolution = summary_text.get("resolution_summary", resolution)
            action_taken = summary_text.get("action_taken_summary", action_taken)

        return {
            "ticket_id": bundle.ticket_id,
            "ticket_number": bundle.ticket_number,
            "root_cause_summary": root_cause,
            "resolution_summary": resolution,
            "action_taken_summary": action_taken,
            "category": category,
            "confidence": confidence,
            "key_keywords": keywords,
            "suggested_tags": self.suggest_tags(bundle, keywords),
            "source_text": combined_text,
        }

    def extract_root_cause(self, bundle: DefectTextBundle) -> str:
        text = _safe_join([bundle.description, bundle.work_notes, bundle.comments[0] if bundle.comments else ""])
        sentences = _sentences(text)
        if not sentences:
            return "Root cause not explicitly stated in the available notes."

        root_cause_patterns = ("root cause", "because", "due to", "caused by", "failed because", "issue was")
        for sentence in sentences:
            lowered = sentence.lower()
            if any(pattern in lowered for pattern in root_cause_patterns):
                return sentence[:320]

        return sentences[0][:320]

    def extract_resolution(self, bundle: DefectTextBundle) -> str:
        text = _safe_join([bundle.close_notes, bundle.work_notes])
        sentences = _sentences(text)
        if not sentences:
            return "No resolution note captured yet."

        resolution_patterns = (
            "resolved",
            "fixed",
            "patched",
            "rolled back",
            "restarted",
            "updated",
            "deployed",
            "mitigated",
        )
        for sentence in sentences:
            lowered = sentence.lower()
            if any(pattern in lowered for pattern in resolution_patterns):
                return sentence[:320]

        return sentences[-1][:320]

    def extract_action_taken(self, bundle: DefectTextBundle) -> str:
        text = _safe_join([bundle.work_notes, bundle.close_notes])
        if not text:
            return "Escalate for manual triage and confirm ownership."

        sentences = _sentences(text)
        if len(sentences) >= 2:
            return sentences[1][:320]
        return sentences[0][:320]

    def classify_category(self, bundle: DefectTextBundle, keywords: list[str]) -> str:
        lower_text = self.compose_document(bundle)
        category_map = {
            "access": "Access & Identity",
            "login": "Access & Identity",
            "payment": "Commerce & Billing",
            "checkout": "Commerce & Billing",
            "api": "Platform & Integration",
            "gateway": "Platform & Integration",
            "database": "Data & Storage",
            "etl": "Data & Analytics",
            "notification": "Messaging & Alerts",
            "report": "Reporting & Analytics",
            "search": "Search & Discovery",
            "mobile": "Mobile Experience",
        }

        for token, category in category_map.items():
            if token in lower_text:
                return category

        if keywords:
            return keywords[0].replace("_", " ").title()

        return "General"

    def estimate_confidence(self, bundle: DefectTextBundle, keywords: list[str]) -> float:
        signal_count = sum(
            bool(value)
            for value in [bundle.description, bundle.work_notes, bundle.close_notes, bundle.comments]
        )
        score = 0.45 + 0.08 * signal_count + 0.04 * min(len(keywords), 5)
        return round(min(score, 0.96), 2)

    def suggest_tags(self, bundle: DefectTextBundle, keywords: list[str]) -> list[str]:
        tags = {token.replace("_", "-") for token in keywords[:5]}
        if bundle.ticket_number:
            tags.add("service-now")
        if bundle.work_notes:
            tags.add("work-notes")
        if bundle.close_notes:
            tags.add("closure")
        return sorted(tags)[:8]

    def _summarize_with_huggingface(self, text: str) -> dict[str, str] | None:
        summarizer = self._summarizer_pipeline()
        if summarizer is None:
            return None

        normalized = self.preprocess_text(text)
        if len(normalized.split()) < 35:
            return None

        generated = summarizer(normalized[:3500], max_length=120, min_length=20, do_sample=False)
        summary_text = generated[0]["summary_text"] if generated else ""
        if not summary_text:
            return None

        return {
            "root_cause_summary": summary_text[:240],
            "resolution_summary": summary_text[:240],
            "action_taken_summary": summary_text[:240],
        }

    # ---------------------------------------------------------------------
    # Clustering / topic modeling / visualization
    # ---------------------------------------------------------------------
    def cluster_documents(self, documents: list[Any], n_clusters: int = 5) -> dict[str, Any]:
        bundles = self.preprocess_documents(documents)
        texts = [self.compose_document(bundle) for bundle in bundles]
        if not texts:
            return {"clusters": [], "visualization": [], "document_count": 0}

        embeddings = self.embed_texts(texts)
        cluster_count = max(1, min(n_clusters, len(texts)))
        model = KMeans(n_clusters=cluster_count, n_init=10, random_state=42)
        labels = model.fit_predict(embeddings)
        reduced = PCA(n_components=2, random_state=42).fit_transform(embeddings)

        cluster_groups: dict[int, list[int]] = {}
        for index, label in enumerate(labels):
            cluster_groups.setdefault(int(label), []).append(index)

        clusters: list[dict[str, Any]] = []
        visualization: list[dict[str, Any]] = []
        for label, member_indices in cluster_groups.items():
            member_texts = [texts[index] for index in member_indices]
            keywords = self.keyword_extractor.extract(" ".join(member_texts))
            sample_titles = [bundles[index].title for index in member_indices[:5]]
            cluster_centroid = model.cluster_centers_[label]
            avg_similarity = float(np.mean(np.dot(embeddings[member_indices], cluster_centroid)))
            clusters.append(
                {
                    "cluster_id": label,
                    "title": self.cluster_title(keywords, label),
                    "defect_count": len(member_indices),
                    "avg_similarity": round(avg_similarity, 4),
                    "keywords": keywords[:8],
                    "sample_titles": sample_titles,
                }
            )
            for member_index in member_indices:
                visualization.append(
                    {
                        "ticket_id": bundles[member_index].ticket_id,
                        "title": bundles[member_index].title,
                        "cluster_id": label,
                        "x": float(reduced[member_index][0]),
                        "y": float(reduced[member_index][1]),
                        "score": float(np.dot(embeddings[member_index], cluster_centroid)),
                    }
                )

        return {"clusters": clusters, "visualization": visualization, "document_count": len(texts)}

    def cluster_title(self, keywords: list[str], cluster_id: int) -> str:
        if keywords:
            return f"{keywords[0].replace('_', ' ').title()} Cluster"
        return f"Cluster {cluster_id + 1}"

    def topic_model(self, documents: list[Any], top_n_words: int = 5) -> dict[str, Any]:
        bundles = self.preprocess_documents(documents)
        texts = [self.compose_document(bundle) for bundle in bundles]
        if not texts:
            return {"topics": [], "document_count": 0}

        if BERTopic is not None and len(texts) >= max(4, settings.BERTOPIC_MIN_TOPIC_SIZE):
            topic_model = BERTopic(
                embedding_model=None,
                vectorizer_model=CountVectorizer(stop_words="english", ngram_range=settings.BERTOPIC_N_GRAM_RANGE),
                min_topic_size=min(settings.BERTOPIC_MIN_TOPIC_SIZE, len(texts)),
                calculate_probabilities=True,
                verbose=False,
            )
            embeddings = self.embed_texts(texts)
            topics, _ = topic_model.fit_transform(texts, embeddings=embeddings)
            topic_info = topic_model.get_topic_info()
            topic_rows: list[dict[str, Any]] = []
            for _, row in topic_info.iterrows():
                topic_id = int(row["Topic"])
                if topic_id == -1:
                    continue
                words = [word for word, _ in (topic_model.get_topic(topic_id) or [])[:top_n_words]]
                representative = next(
                    (texts[index] for index, assigned_topic in enumerate(topics) if int(assigned_topic) == topic_id),
                    None,
                )
                topic_rows.append(
                    {
                        "topic_id": topic_id,
                        "label": str(row["Name"]),
                        "count": int(row["Count"]),
                        "keywords": words,
                        "representative_text": representative[:240] if representative else None,
                    }
                )
            return {"topics": topic_rows, "document_count": len(texts)}

        vectorizer = TfidfVectorizer(stop_words="english", max_features=5000, ngram_range=(1, 2))
        matrix = vectorizer.fit_transform(texts)
        cluster_count = max(1, min(5, len(texts)))
        model = KMeans(n_clusters=cluster_count, n_init=10, random_state=42)
        labels = model.fit_predict(matrix)
        feature_names = vectorizer.get_feature_names_out()

        topics: list[dict[str, Any]] = []
        for cluster_id in sorted(set(labels)):
            member_indices = [index for index, label in enumerate(labels) if label == cluster_id]
            centroid = model.cluster_centers_[cluster_id]
            top_indices = np.argsort(centroid)[::-1][:top_n_words]
            keywords = [feature_names[index] for index in top_indices]
            representative = texts[member_indices[0]] if member_indices else None
            topics.append(
                {
                    "topic_id": int(cluster_id),
                    "label": self.cluster_title(keywords, cluster_id),
                    "count": len(member_indices),
                    "keywords": keywords,
                    "representative_text": representative[:240] if representative else None,
                }
            )

        return {"topics": topics, "document_count": len(texts)}

    # ---------------------------------------------------------------------
    # Batch processing
    # ---------------------------------------------------------------------
    def batch_process(self, documents: list[Any]) -> dict[str, Any]:
        bundles = self.preprocess_documents(documents)
        summaries = [self.summarize(bundle) for bundle in bundles]
        index_result = self.index_documents(documents)
        cluster_result = self.cluster_documents(documents)
        topic_result = self.topic_model(documents)
        return {
            "document_count": len(bundles),
            "indexed_documents": index_result["indexed_documents"],
            "vector_count": index_result["vector_count"],
            "summaries": summaries,
            "clusters": cluster_result["clusters"],
            "visualization": cluster_result["visualization"],
            "topics": topic_result["topics"],
            "faiss_index_path": index_result["faiss_index_path"],
            "metadata_path": index_result["metadata_path"],
        }
