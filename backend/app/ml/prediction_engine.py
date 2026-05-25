"""Production ML prediction engine for DefectIQ AI."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    roc_auc_score,
)
from sklearn.model_selection import KFold, StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, OrdinalEncoder, LabelEncoder

from app.core.config import settings

try:  # pragma: no cover - optional production dependency
    from lightgbm import LGBMClassifier, LGBMRegressor
except Exception:  # pragma: no cover
    LGBMClassifier = None
    LGBMRegressor = None

try:  # pragma: no cover - optional production dependency
    from shap import TreeExplainer
except Exception:  # pragma: no cover
    TreeExplainer = None

try:  # pragma: no cover - optional production dependency
    from xgboost import XGBClassifier, XGBRegressor
except Exception:  # pragma: no cover
    XGBClassifier = None
    XGBRegressor = None


MODEL_NAMES = ("sla_breach", "resolution_time", "assignment", "escalation_risk")


@dataclass(slots=True)
class PredictionArtifact:
    name: str
    model_version: str
    pipeline: Pipeline
    feature_names: list[str]
    metrics: dict[str, float] = field(default_factory=dict)
    cross_validation: dict[str, float] = field(default_factory=dict)
    trained_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    label_encoder: LabelEncoder | None = None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        parsed = pd.to_datetime(value, utc=True)
        if pd.isna(parsed):
            return None
        return parsed.to_pydatetime()
    except Exception:
        return None


def _hours_between(later: datetime | None, earlier: datetime | None) -> float | None:
    if later is None or earlier is None:
        return None
    delta = later - earlier
    return max(delta.total_seconds() / 3600.0, 0.0)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return default
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


class FeatureEngineer:
    def __init__(self, embedding_dimension: int | None = None) -> None:
        self.embedding_dimension = embedding_dimension or settings.EMBEDDING_DIMENSION

    def transform_record(self, record: Any) -> dict[str, Any]:
        if hasattr(record, "model_dump"):
            data = record.model_dump()
        elif isinstance(record, dict):
            data = dict(record)
        else:
            data = {
                key: getattr(record, key, None)
                for key in (
                    "ticket_id",
                    "ticket_number",
                    "priority",
                    "assignment_group",
                    "service_offering",
                    "aging_days",
                    "reassignment_count",
                    "reopen_count",
                    "state",
                    "previous_state",
                    "current_state",
                    "state_transition_count",
                    "work_notes_count",
                    "work_notes_length",
                    "close_notes_length",
                    "comments_count",
                    "first_response_hours",
                    "hours_since_last_update",
                    "opened_at",
                    "closed_at",
                    "first_response_at",
                    "last_modified",
                    "nlp_embeddings",
                    "work_notes_metadata",
                    "state_transitions",
                )
            }

        opened_at = _parse_datetime(data.get("opened_at"))
        closed_at = _parse_datetime(data.get("closed_at"))
        first_response_at = _parse_datetime(data.get("first_response_at"))
        last_modified = _parse_datetime(data.get("last_modified"))

        current_time = _utc_now()
        days_since_open = _hours_between(current_time, opened_at) / 24.0 if opened_at else _safe_float(data.get("aging_days"), 0.0)
        cycle_hours = _hours_between(closed_at, opened_at)
        update_hours = _hours_between(current_time, last_modified)

        embeddings = list(data.get("nlp_embeddings") or [])[: self.embedding_dimension]
        if len(embeddings) < self.embedding_dimension:
            embeddings = embeddings + [0.0] * (self.embedding_dimension - len(embeddings))

        transformed = {
            "priority": (data.get("priority") or "Unknown").strip() if isinstance(data.get("priority"), str) else data.get("priority") or "Unknown",
            "assignment_group": (data.get("assignment_group") or "Unassigned").strip() if isinstance(data.get("assignment_group"), str) else data.get("assignment_group") or "Unassigned",
            "service_offering": (data.get("service_offering") or "Unknown").strip() if isinstance(data.get("service_offering"), str) else data.get("service_offering") or "Unknown",
            "state": (data.get("state") or data.get("current_state") or "Unknown").strip() if isinstance(data.get("state") or data.get("current_state"), str) else data.get("state") or data.get("current_state") or "Unknown",
            "previous_state": (data.get("previous_state") or "Unknown").strip() if isinstance(data.get("previous_state"), str) else data.get("previous_state") or "Unknown",
            "current_state": (data.get("current_state") or data.get("state") or "Unknown").strip() if isinstance(data.get("current_state") or data.get("state"), str) else data.get("current_state") or data.get("state") or "Unknown",
            "aging_days": _safe_float(data.get("aging_days"), days_since_open or 0.0),
            "reassignment_count": _safe_int(data.get("reassignment_count"), 0),
            "reopen_count": _safe_int(data.get("reopen_count"), 0),
            "state_transition_count": _safe_int(data.get("state_transition_count"), len(data.get("state_transitions") or [])),
            "work_notes_count": _safe_int(data.get("work_notes_count"), len((data.get("work_notes_metadata") or {}).get("notes", [])) if isinstance(data.get("work_notes_metadata"), dict) else 0),
            "work_notes_length": _safe_int(data.get("work_notes_length"), 0),
            "close_notes_length": _safe_int(data.get("close_notes_length"), 0),
            "comments_count": _safe_int(data.get("comments_count"), 0),
            "first_response_hours": _safe_float(data.get("first_response_hours"), _hours_between(first_response_at, opened_at) or 0.0),
            "hours_since_last_update": _safe_float(data.get("hours_since_last_update"), update_hours or 0.0),
            "days_since_open": _safe_float(days_since_open, 0.0),
            "cycle_time_hours": _safe_float(cycle_hours, 0.0),
        }

        for index, value in enumerate(embeddings):
            transformed[f"nlp_embedding_{index}"] = float(value)

        return transformed

    def transform_frame(self, records: list[Any]) -> pd.DataFrame:
        transformed_records = [self.transform_record(record) for record in records]
        return pd.DataFrame(transformed_records)


class ExplainabilityEngine:
    def __init__(self) -> None:
        self.available = TreeExplainer is not None

    def feature_importance(self, artifact: PredictionArtifact, top_n: int = 15) -> list[dict[str, float]]:
        estimator = artifact.pipeline.named_steps["model"]
        importance_values = getattr(estimator, "feature_importances_", None)
        if importance_values is None:
            return []
        pairs = sorted(zip(artifact.feature_names, importance_values, strict=False), key=lambda item: item[1], reverse=True)
        return [{"feature": name, "importance": float(score)} for name, score in pairs[:top_n]]

    def shap_values(self, artifact: PredictionArtifact, features: pd.DataFrame, top_n: int = 10) -> list[float] | None:
        if not self.available or features.empty:
            return None
        try:
            preprocessed = artifact.pipeline.named_steps["preprocessor"].transform(features)
            explainer = TreeExplainer(artifact.pipeline.named_steps["model"])
            shap_values = explainer.shap_values(preprocessed)
            values = shap_values[0] if isinstance(shap_values, list) else shap_values
            if values is None:
                return None
            return [float(value) for value in np.mean(np.abs(values), axis=0)[:top_n]]
        except Exception:
            return None


class DefectPredictionEngine:
    def __init__(self, model_dir: str | None = None) -> None:
        self.model_dir = Path(model_dir or settings.MODEL_DIR) / "predictions"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.feature_engineer = FeatureEngineer()
        self.explainability = ExplainabilityEngine()
        self.artifacts: dict[str, PredictionArtifact] = {}
        self.assignment_encoder = LabelEncoder()

    @property
    def categorical_features(self) -> list[str]:
        return ["priority", "assignment_group", "service_offering", "state", "previous_state", "current_state"]

    @property
    def numeric_features(self) -> list[str]:
        base = [
            "aging_days",
            "reassignment_count",
            "reopen_count",
            "state_transition_count",
            "work_notes_count",
            "work_notes_length",
            "close_notes_length",
            "comments_count",
            "first_response_hours",
            "hours_since_last_update",
            "days_since_open",
            "cycle_time_hours",
        ]
        return base + [f"nlp_embedding_{index}" for index in range(self.feature_engineer.embedding_dimension)]

    def _build_preprocessor(self) -> ColumnTransformer:
        categorical_pipe = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]
        )
        numeric_pipe = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
            ]
        )
        return ColumnTransformer(
            transformers=[
                ("categorical", categorical_pipe, self.categorical_features),
                ("numeric", numeric_pipe, self.numeric_features),
            ],
            remainder="drop",
            verbose_feature_names_out=False,
        )

    def _build_classifier(self, class_weight: str | dict[str, float] | None = "balanced"):
        if LGBMClassifier is not None:
            return LGBMClassifier(
                n_estimators=300,
                learning_rate=0.05,
                num_leaves=31,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=42,
                class_weight=class_weight,
            )
        if XGBClassifier is not None:
            return XGBClassifier(
                n_estimators=300,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=42,
                n_jobs=1,
            )
        return RandomForestClassifier(n_estimators=300, random_state=42, class_weight=class_weight)

    def _build_regressor(self):
        if LGBMRegressor is not None:
            return LGBMRegressor(n_estimators=400, learning_rate=0.05, num_leaves=31, random_state=42)
        if XGBRegressor is not None:
            return XGBRegressor(
                n_estimators=400,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=42,
                n_jobs=1,
            )
        return RandomForestRegressor(n_estimators=300, random_state=42)

    def _build_pipeline(self, estimator) -> Pipeline:
        return Pipeline(steps=[("preprocessor", self._build_preprocessor()), ("model", estimator)])

    def _safe_classification_cv(self, labels: list[Any]) -> StratifiedKFold | None:
        sample_count = len(labels)
        if sample_count < 4:
            return None
        _, counts = np.unique(labels, return_counts=True)
        if counts.size == 0 or counts.min() < 2:
            return None
        splits = min(5, sample_count, int(counts.min()))
        return StratifiedKFold(n_splits=max(2, splits), shuffle=True, random_state=42)

    def _safe_regression_cv(self, labels: list[Any]) -> KFold | None:
        if len(labels) < 4:
            return None
        return KFold(n_splits=min(5, len(labels)), shuffle=True, random_state=42)

    def _fit_model(self, name: str, pipeline: Pipeline, features: pd.DataFrame, target: np.ndarray, scoring: str, cv):
        cross_scores = cross_validate(pipeline, features, target, cv=cv, scoring=scoring, error_score="raise")
        pipeline.fit(features, target)
        return pipeline, cross_scores

    def _feature_columns(self, features: pd.DataFrame) -> list[str]:
        fitted = self._build_preprocessor().fit(features)
        return list(fitted.get_feature_names_out())

    def _persist_artifact(self, artifact: PredictionArtifact) -> str:
        path = self.model_dir / f"{artifact.name}_{artifact.model_version}.joblib"
        joblib.dump(artifact, path)
        registry_path = self.model_dir / "registry.json"
        registry: dict[str, Any] = {}
        if registry_path.exists():
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry[artifact.name] = {
            "model_version": artifact.model_version,
            "path": str(path),
            "metrics": artifact.metrics,
            "cross_validation": artifact.cross_validation,
            "trained_at": artifact.trained_at.isoformat(),
        }
        registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
        return str(path)

    def _make_artifact(self, name: str, model_version: str, pipeline: Pipeline, features: pd.DataFrame, metrics: dict[str, float], cross_validation: dict[str, float], label_encoder: LabelEncoder | None = None) -> PredictionArtifact:
        feature_names = list(pipeline.named_steps["preprocessor"].fit(features).get_feature_names_out())
        return PredictionArtifact(
            name=name,
            model_version=model_version,
            pipeline=pipeline,
            feature_names=feature_names,
            metrics=metrics,
            cross_validation=cross_validation,
            label_encoder=label_encoder,
        )

    def train(
        self,
        examples: list[Any],
        labels: dict[str, list[Any]],
        model_version: str = "v1",
    ) -> dict[str, Any]:
        features = self.feature_engineer.transform_frame(examples)
        self.artifacts = {}

        if len(features) < 2:
            raise ValueError("At least two training examples are required.")

        indices = np.arange(len(features))
        if len(features) >= 5:
            train_indices, test_indices = train_test_split(
                indices,
                test_size=0.2,
                random_state=42,
                stratify=labels["sla_breached"] if len(set(labels["sla_breached"])) > 1 else None,
            )
        else:
            train_indices = test_indices = indices

        x_train = features.iloc[train_indices]
        x_test = features.iloc[test_indices]

        y_sla_train = np.array(labels["sla_breached"])[train_indices]
        y_sla_test = np.array(labels["sla_breached"])[test_indices]
        sla_pipeline = self._build_pipeline(self._build_classifier())
        sla_cv = self._safe_classification_cv(labels["sla_breached"])
        sla_pipeline.fit(x_train, y_sla_train)
        sla_pred = sla_pipeline.predict(x_test)
        sla_prob = sla_pipeline.predict_proba(x_test)[:, 1]
        sla_metrics = {
            "accuracy": float(accuracy_score(y_sla_test, sla_pred)),
            "f1": float(f1_score(y_sla_test, sla_pred, zero_division=0)),
            "precision": float(precision_score(y_sla_test, sla_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_sla_test, sla_prob)) if len(set(y_sla_test)) > 1 else 0.0,
            "average_precision": float(average_precision_score(y_sla_test, sla_prob)) if len(set(y_sla_test)) > 1 else 0.0,
        }
        sla_cv_scores = cross_validate(self._build_pipeline(self._build_classifier()), features, labels["sla_breached"], cv=sla_cv, scoring={"accuracy": "accuracy", "f1": "f1", "roc_auc": "roc_auc" if len(set(labels["sla_breached"])) > 1 else "accuracy"}, error_score="raise") if sla_cv is not None else {}
        sla_artifact = self._make_artifact(
            "sla_breach",
            model_version,
            sla_pipeline,
            features,
            sla_metrics,
            {key: float(np.mean(value)) for key, value in sla_cv_scores.items() if key.startswith("test_")},
        )
        self.artifacts["sla_breach"] = sla_artifact
        self._persist_artifact(sla_artifact)

        resolution_pipeline = self._build_pipeline(self._build_regressor())
        y_resolution_train = np.array(labels["resolution_hours"])[train_indices]
        y_resolution_test = np.array(labels["resolution_hours"])[test_indices]
        resolution_pipeline.fit(x_train, y_resolution_train)
        resolution_pred = resolution_pipeline.predict(x_test)
        resolution_metrics = {
            "mae": float(mean_absolute_error(y_resolution_test, resolution_pred)),
            "rmse": float(mean_squared_error(y_resolution_test, resolution_pred, squared=False)),
            "r2": float(r2_score(y_resolution_test, resolution_pred)),
        }
        resolution_cv = self._safe_regression_cv(labels["resolution_hours"])
        resolution_cv_scores = cross_validate(self._build_pipeline(self._build_regressor()), features, labels["resolution_hours"], cv=resolution_cv, scoring={"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error", "r2": "r2"}, error_score="raise") if resolution_cv is not None else {}
        resolution_artifact = self._make_artifact(
            "resolution_time",
            model_version,
            resolution_pipeline,
            features,
            resolution_metrics,
            {key: float(np.mean(value)) for key, value in resolution_cv_scores.items() if key.startswith("test_")},
        )
        self.artifacts["resolution_time"] = resolution_artifact
        self._persist_artifact(resolution_artifact)

        self.assignment_encoder.fit(labels["assignment_group"])
        assignment_targets = self.assignment_encoder.transform(labels["assignment_group"])
        assignment_pipeline = self._build_pipeline(self._build_classifier(class_weight=None))
        y_assignment_train = assignment_targets[train_indices]
        y_assignment_test = assignment_targets[test_indices]
        assignment_pipeline.fit(x_train, y_assignment_train)
        assignment_pred = self.assignment_encoder.inverse_transform(assignment_pipeline.predict(x_test))
        assignment_prob = assignment_pipeline.predict_proba(x_test)
        assignment_metrics = {
            "accuracy": float(accuracy_score(self.assignment_encoder.inverse_transform(y_assignment_test), assignment_pred)),
            "f1_macro": float(f1_score(self.assignment_encoder.inverse_transform(y_assignment_test), assignment_pred, average="macro", zero_division=0)),
        }
        assignment_cv = self._safe_classification_cv(labels["assignment_group"])
        assignment_cv_scores = cross_validate(self._build_pipeline(self._build_classifier(class_weight=None)), features, assignment_targets, cv=assignment_cv, scoring={"accuracy": "accuracy", "f1_macro": "f1_macro"}, error_score="raise") if assignment_cv is not None else {}
        assignment_artifact = self._make_artifact(
            "assignment",
            model_version,
            assignment_pipeline,
            features,
            assignment_metrics,
            {key: float(np.mean(value)) for key, value in assignment_cv_scores.items() if key.startswith("test_")},
            label_encoder=self.assignment_encoder,
        )
        self.artifacts["assignment"] = assignment_artifact
        self._persist_artifact(assignment_artifact)

        escalation_pipeline = self._build_pipeline(self._build_classifier())
        y_escalation_train = np.array(labels["escalation_risk"])[train_indices]
        y_escalation_test = np.array(labels["escalation_risk"])[test_indices]
        escalation_pipeline.fit(x_train, y_escalation_train)
        escalation_pred = escalation_pipeline.predict(x_test)
        escalation_prob = escalation_pipeline.predict_proba(x_test)[:, 1]
        escalation_metrics = {
            "accuracy": float(accuracy_score(y_escalation_test, escalation_pred)),
            "f1": float(f1_score(y_escalation_test, escalation_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_escalation_test, escalation_prob)) if len(set(y_escalation_test)) > 1 else 0.0,
        }
        escalation_cv = self._safe_classification_cv(labels["escalation_risk"])
        escalation_cv_scores = cross_validate(self._build_pipeline(self._build_classifier()), features, labels["escalation_risk"], cv=escalation_cv, scoring={"accuracy": "accuracy", "f1": "f1", "roc_auc": "roc_auc" if len(set(labels["escalation_risk"])) > 1 else "accuracy"}, error_score="raise") if escalation_cv is not None else {}
        escalation_artifact = self._make_artifact(
            "escalation_risk",
            model_version,
            escalation_pipeline,
            features,
            escalation_metrics,
            {key: float(np.mean(value)) for key, value in escalation_cv_scores.items() if key.startswith("test_")},
        )
        self.artifacts["escalation_risk"] = escalation_artifact
        self._persist_artifact(escalation_artifact)

        return {
            "model_version": model_version,
            "training_examples": len(features),
            "models": {
                name: {
                    "metrics": artifact.metrics,
                    "cross_validation": artifact.cross_validation,
                    "path": str(self.model_dir / f"{artifact.name}_{artifact.model_version}.joblib"),
                }
                for name, artifact in self.artifacts.items()
            },
        }

    def _load_artifact(self, name: str) -> PredictionArtifact | None:
        artifact = self.artifacts.get(name)
        if artifact is not None:
            return artifact
        registry_path = self.model_dir / "registry.json"
        if not registry_path.exists():
            return None
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        info = registry.get(name)
        if not info:
            return None
        path = Path(info["path"])
        if not path.exists():
            return None
        loaded = joblib.load(path)
        if isinstance(loaded, PredictionArtifact):
            self.artifacts[name] = loaded
            return loaded
        return None

    def _predict_probability(self, artifact: PredictionArtifact, features: pd.DataFrame) -> np.ndarray:
        estimator = artifact.pipeline
        if hasattr(estimator, "predict_proba"):
            return estimator.predict_proba(features)
        return np.zeros((len(features), 2), dtype=float)

    def predict(self, record: Any) -> dict[str, Any]:
        features = self.feature_engineer.transform_frame([record])
        predictions = self.predict_many(features)
        return predictions[0]

    def predict_many(self, records: pd.DataFrame | list[Any]) -> list[dict[str, Any]]:
        features = records if isinstance(records, pd.DataFrame) else self.feature_engineer.transform_frame(records)
        outputs: list[dict[str, Any]] = []
        sla_artifact = self._load_artifact("sla_breach")
        resolution_artifact = self._load_artifact("resolution_time")
        assignment_artifact = self._load_artifact("assignment")
        escalation_artifact = self._load_artifact("escalation_risk")
        model_version = next((artifact.model_version for artifact in [sla_artifact, resolution_artifact, assignment_artifact, escalation_artifact] if artifact is not None), "untrained")

        for index in range(len(features)):
            frame = features.iloc[[index]]
            sla_probability = 0.0
            sla_confidence = 0.0
            assignment_probability = 0.0
            assignment_confidence = 0.0
            escalation_probability = 0.0
            escalation_confidence = 0.0
            resolution_value = 0.0

            if sla_artifact is not None:
                sla_probability = float(sla_artifact.pipeline.predict_proba(frame)[0][1])
                sla_confidence = float(max(sla_probability, 1.0 - sla_probability))
            if resolution_artifact is not None:
                resolution_value = float(max(1.0, resolution_artifact.pipeline.predict(frame)[0]))
            if assignment_artifact is not None:
                assignment_probs = assignment_artifact.pipeline.predict_proba(frame)[0]
                assignment_index = int(np.argmax(assignment_probs))
                assignment_probability = float(assignment_probs[assignment_index])
                assignment_confidence = float(assignment_probability)
                assignment_label = assignment_artifact.label_encoder.inverse_transform([assignment_index])[0] if assignment_artifact.label_encoder is not None else str(assignment_index)
            else:
                assignment_label = "Unassigned"
            if escalation_artifact is not None:
                escalation_probability = float(escalation_artifact.pipeline.predict_proba(frame)[0][1])
                escalation_confidence = float(max(escalation_probability, 1.0 - escalation_probability))

            outputs.append(
                {
                    "sla_breach": {
                        "label": "Breach" if sla_probability >= 0.5 else "No Breach",
                        "probability": sla_probability,
                        "confidence": sla_confidence,
                    },
                    "resolution_time": {
                        "label": "Resolution Time",
                        "value": resolution_value,
                        "confidence": 0.75,
                    },
                    "assignment": {
                        "label": assignment_label,
                        "probability": assignment_probability,
                        "confidence": assignment_confidence,
                    },
                    "escalation_risk": {
                        "label": "High Risk" if escalation_probability >= 0.5 else "Lower Risk",
                        "probability": escalation_probability,
                        "confidence": escalation_confidence,
                    },
                    "model_version": model_version,
                    "raw_features": frame.iloc[0].to_dict(),
                }
            )
        return outputs

    def explain(self, record: Any, model_name: str | None = None) -> dict[str, Any]:
        features = self.feature_engineer.transform_frame([record])
        target_name = model_name or "sla_breach"
        artifact = self._load_artifact(target_name)
        if artifact is None:
            return {"model_name": target_name, "feature_importance": [], "shap_values": None}
        return {
            "model_name": target_name,
            "model_version": artifact.model_version,
            "feature_importance": self.explainability.feature_importance(artifact),
            "shap_values": self.explainability.shap_values(artifact, features),
        }
