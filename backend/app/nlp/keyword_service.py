"""Keyword extraction and trend analysis."""

from __future__ import annotations

from collections import Counter
from typing import Any


class KeywordService:
    @staticmethod
    def extract_keywords(texts: list[str], top_k: int = 10) -> list[dict[str, Any]]:
        cleaned = [text.strip() for text in texts if text and text.strip()]
        if not cleaned:
            return []
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
        except ImportError:
            counts = Counter(word for text in cleaned for word in text.lower().split())
            return [{"keyword": word, "score": float(score)} for word, score in counts.most_common(top_k)]

        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        matrix = vectorizer.fit_transform(cleaned)
        scores = matrix.mean(axis=0).A1
        keywords = vectorizer.get_feature_names_out()
        ranked = sorted(zip(keywords, scores), key=lambda item: item[1], reverse=True)
        return [{"keyword": keyword, "score": round(float(score), 6)} for keyword, score in ranked[:top_k]]

    @staticmethod
    def classify_topic(text: str) -> str:
        normalized = text.lower()
        if any(keyword in normalized for keyword in ["login", "authentication", "session"]):
            return "authentication"
        if any(keyword in normalized for keyword in ["performance", "slow", "latency"]):
            return "performance"
        if any(keyword in normalized for keyword in ["ui", "button", "layout", "css"]):
            return "ui"
        return "general"
