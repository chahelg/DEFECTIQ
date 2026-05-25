"""Training orchestration for ML models."""

from __future__ import annotations

from typing import Any

from app.ml.prediction_engine import DefectPredictionEngine


class ModelTrainer:
    def __init__(self, engine: DefectPredictionEngine | None = None) -> None:
        self.engine = engine or DefectPredictionEngine()

    def train_all(self, examples: list[Any], labels: dict[str, list[Any]], model_version: str = "v1") -> dict[str, Any]:
        return self.engine.train(examples, labels, model_version=model_version)

    def train_sla_model(self, examples: list[Any], labels: list[int], model_version: str = "v1") -> dict[str, Any]:
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

    def train_time_model(self, examples: list[Any], labels: list[float], model_version: str = "v1") -> dict[str, Any]:
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

    def train_assignment_model(self, examples: list[Any], labels: list[str], model_version: str = "v1") -> dict[str, Any]:
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

    def train_escalation_model(self, examples: list[Any], labels: list[int], model_version: str = "v1") -> dict[str, Any]:
        return self.engine.train(
            examples,
            {
                "sla_breached": [0 for _ in examples],
                "resolution_hours": [0.0 for _ in examples],
                "assignment_group": ["Unassigned" for _ in examples],
                "escalation_risk": labels,
            },
            model_version=model_version,
        )
