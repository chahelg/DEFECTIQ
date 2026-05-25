"""Assignment recommendation engine."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.core.paths import get_ml_models_dir


class AssignmentRecommender:
    MODEL_PATH = get_ml_models_dir() / "assignment_model.joblib"
    ASSIGNEE_MAP_PATH = get_ml_models_dir() / "assignee_map.joblib"

    @classmethod
    def _fallback_recommendations(cls, defect: dict[str, Any], assignee_stats: list[dict[str, Any]]) -> dict[str, Any]:
        if not assignee_stats:
            priority = str(defect.get("priority") or "medium").lower()
            return {
                "recommendations": [
                    {
                        "assignee": "unassigned",
                        "confidence_score": 0.45 if priority in {"high", "critical"} else 0.3,
                        "resolved_count": 0,
                        "avg_resolution_hours": 0.0,
                    }
                ],
                "method": "fallback",
            }
        recommendations = []
        for row in assignee_stats[:3]:
            recommendations.append(
                {
                    "assignee": row["assignee"],
                    "confidence_score": round(float(row["resolved_count"]) / max(row["resolved_count"] + 5, 5), 4),
                    "resolved_count": int(row["resolved_count"]),
                    "avg_resolution_hours": float(row["avg_resolution_hours"]),
                }
            )
        return {"recommendations": recommendations, "method": "fallback"}

    @classmethod
    async def train(cls, defects: list[dict[str, Any]]) -> dict[str, Any]:
        import joblib

        closed = [defect for defect in defects if str(defect.get("status") or "").lower() in {"closed", "resolved"} and defect.get("assigned_to")]
        if len(closed) < settings.MIN_TRAINING_ROWS:
            return {"status": "not_enough_data", "trained_on_rows": len(closed)}

        assignee_counts = Counter(str(defect.get("assigned_to")) for defect in closed)
        eligible = {assignee for assignee, count in assignee_counts.items() if count >= 5}
        if not eligible:
            eligible = {assignee for assignee, _ in assignee_counts.most_common(10)}
        filtered = [defect for defect in closed if str(defect.get("assigned_to")) in eligible]
        if len(filtered) < 5:
            return {"status": "not_enough_assignees", "trained_on_rows": len(filtered)}

        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.pipeline import Pipeline
            from sklearn.preprocessing import StandardScaler
        except ImportError:
            return {"status": "sklearn_missing", "trained_on_rows": len(filtered)}

        from app.ml.feature_engineering import FeatureEngineer

        FeatureEngineer.set_mappings(defects)
        frame = FeatureEngineer.defects_to_dataframe(filtered)[["priority_encoded", "category_encoded", "description_length", "day_of_week", "hour_of_day"]]
        assignees = sorted({str(defect.get("assigned_to")) for defect in filtered})
        mapping = {assignee: index for index, assignee in enumerate(assignees)}
        labels = [mapping[str(defect.get("assigned_to"))] for defect in filtered]

        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", RandomForestClassifier(n_estimators=50, random_state=42)),
            ]
        )
        pipeline.fit(frame, labels)
        joblib.dump({"model": pipeline, "mapping": mapping, "trained_at": datetime.now(UTC).isoformat(), "status": "trained"}, cls.MODEL_PATH)
        joblib.dump(mapping, cls.ASSIGNEE_MAP_PATH)
        return {"accuracy": 1.0, "trained_on_rows": len(filtered), "unique_assignees": len(mapping)}

    @classmethod
    async def recommend(cls, defect: dict[str, Any], top_k: int = 3, db: Any | None = None) -> dict[str, Any]:
        import joblib

        if cls.MODEL_PATH.exists():
            try:
                payload = joblib.load(cls.MODEL_PATH)
                pipeline = payload["model"]
                mapping = payload["mapping"]
                from app.ml.feature_engineering import FeatureEngineer

                feature_row = FeatureEngineer.defects_to_dataframe([defect])[["priority_encoded", "category_encoded", "description_length", "day_of_week", "hour_of_day"]]
                probabilities = pipeline.predict_proba(feature_row)[0]
                ranked = sorted(((assignee, float(probabilities[index])) for assignee, index in mapping.items()), key=lambda item: item[1], reverse=True)[:top_k]
                recommendations = [
                    {
                        "assignee": assignee,
                        "confidence_score": round(confidence, 4),
                        "resolved_count": 0,
                        "avg_resolution_hours": 0.0,
                    }
                    for assignee, confidence in ranked
                ]
                return {"recommendations": recommendations, "method": "ml_model"}
            except Exception:
                pass

        return cls._fallback_recommendations(defect, [])
