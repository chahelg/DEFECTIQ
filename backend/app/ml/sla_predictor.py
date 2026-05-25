"""SLA breach predictor with ML and heuristic fallbacks."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.core.paths import get_ml_models_dir


class SLAPredictor:
    MODEL_PATH = get_ml_models_dir() / "sla_model.joblib"

    @classmethod
    def _rule_based_prediction(cls, defect: dict[str, Any]) -> dict[str, Any]:
        from app.ml.feature_engineering import FeatureEngineer

        score = 0.0
        priority = str(defect.get("priority") or "").strip().lower()
        if priority == "critical":
            score += 0.4
        if priority == "high":
            score += 0.2
        if float(FeatureEngineer.extract_features(defect)["age_hours"]) > 48:
            score += 0.2
        if int(defect.get("reopen_count") or 0) > 1:
            score += 0.2
        return {
            "sla_breach_probability": round(min(score, 0.95), 4),
            "breach_risk_level": "Critical" if score > 0.7 else "High" if score > 0.5 else "Medium" if score > 0.3 else "Low",
            "confidence": "low",
            "top_risk_factors": ["priority", "age_hours", "reopen_count"],
            "method": "rule_based",
        }

    @classmethod
    async def train(cls, defects: list[dict[str, Any]]) -> dict[str, Any]:
        import joblib

        if len(defects) < settings.MIN_TRAINING_ROWS:
            return {"status": "not_enough_data", "trained_on_rows": len(defects)}

        try:
            from xgboost import XGBClassifier
        except ImportError:
            return {"status": "xgboost_missing", "trained_on_rows": len(defects)}

        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from app.ml.feature_engineering import FeatureEngineer

        FeatureEngineer.set_mappings(defects)
        frame = FeatureEngineer.defects_to_dataframe(defects)
        labels = [1 if bool(defect.get("is_sla_breached")) else 0 for defect in defects]

        if len(set(labels)) < 2:
            return {"status": "single_class", "trained_on_rows": len(defects)}

        x_train, x_test, y_train, y_test = train_test_split(frame, labels, test_size=0.2, random_state=42, stratify=labels)

        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "model",
                    XGBClassifier(
                        n_estimators=100,
                        max_depth=4,
                        learning_rate=0.1,
                        random_state=42,
                        eval_metric="logloss",
                    ),
                ),
            ]
        )
        pipeline.fit(x_train, y_train)

        predictions = pipeline.predict(x_test)
        probabilities = pipeline.predict_proba(x_test)[:, 1]
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
            "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
            "f1": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4) if len(set(y_test)) > 1 else 0.0,
        }
        payload = {
            "model": pipeline,
            "metrics": metrics,
            "trained_at": datetime.now(UTC).isoformat(),
            "feature_names": FeatureEngineer.get_feature_names(),
            "status": "trained",
        }
        joblib.dump(payload, cls.MODEL_PATH)
        return {**metrics, "trained_on_rows": len(defects), "model_version": payload["trained_at"]}

    @classmethod
    async def predict(cls, defect: dict[str, Any]) -> dict[str, Any]:
        import joblib

        if not cls.MODEL_PATH.exists():
            return cls._rule_based_prediction(defect)

        try:
            payload = joblib.load(cls.MODEL_PATH)
            pipeline = payload["model"]
        except Exception:
            return cls._rule_based_prediction(defect)

        from app.ml.feature_engineering import FeatureEngineer

        features = FeatureEngineer.defects_to_dataframe([defect])
        probability = float(pipeline.predict_proba(features)[0][1])
        if probability > 0.7:
            risk = "Critical"
        elif probability > 0.5:
            risk = "High"
        elif probability > 0.3:
            risk = "Medium"
        else:
            risk = "Low"

        model = pipeline.named_steps.get("model")
        importances = getattr(model, "feature_importances_", [])
        ranked = sorted(zip(FeatureEngineer.get_feature_names(), importances), key=lambda item: item[1], reverse=True)
        return {
            "sla_breach_probability": round(probability, 4),
            "breach_risk_level": risk,
            "confidence": "high" if probability > 0.65 or probability < 0.35 else "medium",
            "top_risk_factors": [name for name, _ in ranked[:3]],
            "method": "ml_model",
        }

    @classmethod
    async def predict_batch(cls, defects: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [await cls.predict(defect) for defect in defects]

    @classmethod
    async def get_model_info(cls) -> dict[str, Any]:
        import joblib

        if not cls.MODEL_PATH.exists():
            return {"status": "not_trained"}

        payload = joblib.load(cls.MODEL_PATH)
        return {
            "status": payload.get("status", "trained"),
            "trained_at": payload.get("trained_at"),
            "metrics": payload.get("metrics"),
            "exists": True,
        }
