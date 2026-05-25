"""Escalation risk predictor wrapper."""

from __future__ import annotations

from typing import Any

from app.ml.prediction_engine import DefectPredictionEngine


class EscalationRiskPredictor:
    def __init__(self, engine: DefectPredictionEngine | None = None) -> None:
        self.engine = engine or DefectPredictionEngine()

    def fit(self, examples: list[Any], labels: list[int], model_version: str = "v1") -> dict[str, Any]:
        return self.engine.train(
            examples,
            {
                "sla_breached": labels,
                "resolution_hours": [0.0 for _ in examples],
                "assignment_group": ["Unassigned" for _ in examples],
                "escalation_risk": labels,
            },
            model_version=model_version,
        )

    def predict_probability(self, features: Any) -> float:
        return float(self.engine.predict(features)["escalation_risk"]["probability"])
