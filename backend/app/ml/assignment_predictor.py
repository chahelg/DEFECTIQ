"""Assignment recommendation predictor using the shared DefectIQ prediction engine."""

from __future__ import annotations

from typing import Any

from app.ml.prediction_engine import DefectPredictionEngine


class AssignmentPredictor:
    def __init__(self, engine: DefectPredictionEngine | None = None) -> None:
        self.engine = engine or DefectPredictionEngine()

    def fit(self, examples: list[Any], labels: list[str], model_version: str = "v1") -> dict[str, Any]:
        return self.engine.train(
            examples,
            {
                "sla_breached": [0 for _ in examples],
                "resolution_hours": [0.0 for _ in examples],
                "assignment_group": labels,
                "escalation_risk": [0 for _ in examples],
            },
            model_version=model_version,
        )

    def predict_group(self, features: Any) -> str:
        return str(self.engine.predict(features)["assignment"]["label"])
