"""Keyword extraction utilities."""

from __future__ import annotations

from sklearn.feature_extraction.text import CountVectorizer


class KeywordExtractor:
    def __init__(self) -> None:
        self.vectorizer = CountVectorizer(stop_words="english", max_features=20)

    def extract(self, text: str) -> list[str]:
        if not text.strip():
            return []
        matrix = self.vectorizer.fit_transform([text])
        keywords = self.vectorizer.get_feature_names_out()
        return list(keywords[: min(10, len(keywords))])
