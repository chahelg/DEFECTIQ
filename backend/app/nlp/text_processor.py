"""Text preprocessing utilities."""

from __future__ import annotations

import re

from sklearn.feature_extraction.text import TfidfVectorizer


class TextProcessor:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)

    def normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text
