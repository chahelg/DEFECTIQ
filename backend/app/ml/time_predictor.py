"""Resolution time predictor using the shared DefectIQ prediction engine."""

from __future__ import annotations

from typing import Any

from app.ml.prediction_engine import DefectPredictionEngine


class TimePredictor:
    def __init__(self, engine: DefectPredictionEngine | None = None) -> None:
        self.engine = engine or DefectPredictionEngine()

    def fit(self, examples: list[Any], labels: list[float], model_version: str = "v1") -> dict[str, Any]:
        return self.engine.train(
            examples,
            {
                "sla_breached": [0 for _ in examples],
                "resolution_hours": labels,
                "assignment_group": ["Unassigned" for _ in examples],
                "escalation_risk": [0 for _ in examples],
            },
            model_version=model_version,
        )

    def predict_hours(self, features: Any) -> int:
        return int(round(self.engine.predict(features)["resolution_time"]["value"] or 1))
