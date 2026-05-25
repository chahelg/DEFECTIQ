"""Feature engineering utilities for predictive models."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class FeatureEngineer:
    PRIORITY_MAP = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    STATUS_MAP: dict[str, int] = {}
    CATEGORY_MAP: dict[str, int] = {}

    @classmethod
    def set_mappings(cls, defects: list[dict[str, Any]]) -> None:
        statuses = sorted({str(defect.get("status") or "unknown").strip().lower() for defect in defects})
        categories = sorted({str(defect.get("category") or "unknown").strip().lower() for defect in defects})
        cls.STATUS_MAP = {status: index + 1 for index, status in enumerate(statuses)}
        cls.CATEGORY_MAP = {category: index + 1 for index, category in enumerate(categories)}

    @classmethod
    def extract_features(cls, defect: dict[str, Any]) -> dict[str, Any]:
        import pandas as pd

        opened_at = pd.to_datetime(defect.get("opened_at"), errors="coerce", utc=True)
        reference_time = pd.to_datetime(defect.get("resolved_at"), errors="coerce", utc=True)
        if pd.isna(opened_at):
            opened_at = pd.Timestamp.now(tz=UTC)
        if pd.isna(reference_time):
            reference_time = pd.Timestamp.now(tz=UTC)

        age_hours = max((reference_time - opened_at).total_seconds() / 3600.0, 0.0)
        priority = str(defect.get("priority") or "unknown").strip().lower()
        status = str(defect.get("status") or "unknown").strip().lower()
        category = str(defect.get("category") or "unknown").strip().lower()
        description = str(defect.get("description") or "")
        title = str(defect.get("title") or "")

        return {
            "age_hours": age_hours,
            "reopen_count": int(defect.get("reopen_count") or 0),
            "description_length": len(description),
            "title_length": len(title),
            "has_resolution_notes": 1 if defect.get("resolution_notes") else 0,
            "priority_encoded": cls.PRIORITY_MAP.get(priority, 0),
            "status_encoded": cls.STATUS_MAP.get(status, 0),
            "category_encoded": cls.CATEGORY_MAP.get(category, 0),
            "day_of_week": int(opened_at.weekday()),
            "hour_of_day": int(opened_at.hour),
            "is_weekend": 1 if opened_at.weekday() >= 5 else 0,
            "month": int(opened_at.month),
        }

    @classmethod
    def get_feature_names(cls) -> list[str]:
        return [
            "age_hours",
            "reopen_count",
            "description_length",
            "title_length",
            "has_resolution_notes",
            "priority_encoded",
            "status_encoded",
            "category_encoded",
            "day_of_week",
            "hour_of_day",
            "is_weekend",
            "month",
        ]

    @classmethod
    def defects_to_dataframe(cls, defects: list[dict[str, Any]]) -> pd.DataFrame:
        import pandas as pd

        if not cls.STATUS_MAP or not cls.CATEGORY_MAP:
            cls.set_mappings(defects)
        rows = [cls.extract_features(defect) for defect in defects]
        return pd.DataFrame(rows, columns=cls.get_feature_names())
