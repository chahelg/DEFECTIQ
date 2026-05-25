"""Resolution time predictor with ML and fallback heuristics."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings
from app.core.paths import get_ml_models_dir


class ResolutionPredictor:
    MODEL_PATH = get_ml_models_dir() / "resolution_model.joblib"

    @classmethod
    def _fallback(cls, defect: dict[str, Any]) -> dict[str, Any]:
        priority = str(defect.get("priority") or "").strip().lower()
        base_hours = {"critical": 4.0, "high": 8.0, "medium": 24.0, "low": 72.0}.get(priority, 24.0)
        if int(defect.get("reopen_count") or 0) > 0:
            base_hours *= 1.5
        completion = datetime.now(UTC) + timedelta(hours=base_hours)
        return {
            "estimated_hours": round(base_hours, 2),
            "estimated_completion_date": completion.isoformat(),
            "confidence_interval_hours": [round(base_hours * 0.8, 2), round(base_hours * 1.2, 2)],
            "confidence": "low",
            "method": "rule_based",
        }

    @classmethod
    async def train(cls, defects: list[dict[str, Any]]) -> dict[str, Any]:
        import joblib

        closed = [defect for defect in defects if str(defect.get("status") or "").lower() in {"closed", "resolved"} and defect.get("resolved_at")]
        if len(closed) < settings.MIN_TRAINING_ROWS:
            return {"status": "not_enough_data", "trained_on_rows": len(closed)}

        try:
            from xgboost import XGBRegressor
        except ImportError:
            return {"status": "xgboost_missing", "trained_on_rows": len(closed)}

        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from app.ml.feature_engineering import FeatureEngineer

        FeatureEngineer.set_mappings(defects)
        frame = FeatureEngineer.defects_to_dataframe(closed)
        labels = [
            max((datetime.fromisoformat(str(defect["resolved_at"]).replace("Z", "+00:00")) - datetime.fromisoformat(str(defect["opened_at"]).replace("Z", "+00:00"))).total_seconds() / 3600.0, 0.0)
            for defect in closed
        ]

        x_train, x_test, y_train, y_test = train_test_split(frame, labels, test_size=0.2, random_state=42)
        pipeline = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", XGBRegressor(n_estimators=100, max_depth=4, random_state=42)),
            ]
        )
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        rmse = mean_squared_error(y_test, predictions) ** 0.5
        payload = {
            "model": pipeline,
            "metrics": {
                "mae_hours": round(float(mean_absolute_error(y_test, predictions)), 4),
                "rmse_hours": round(float(rmse), 4),
                "r2_score": round(float(r2_score(y_test, predictions)), 4),
            },
            "trained_at": datetime.now(UTC).isoformat(),
            "status": "trained",
        }
        joblib.dump(payload, cls.MODEL_PATH)
        return {**payload["metrics"], "trained_on_rows": len(closed)}

    @classmethod
    async def predict(cls, defect: dict[str, Any]) -> dict[str, Any]:
        import joblib

        if not cls.MODEL_PATH.exists():
            return cls._fallback(defect)

        try:
            payload = joblib.load(cls.MODEL_PATH)
            pipeline = payload["model"]
        except Exception:
            return cls._fallback(defect)

        from app.ml.feature_engineering import FeatureEngineer

        features = FeatureEngineer.defects_to_dataframe([defect])
        estimated_hours = max(float(pipeline.predict(features)[0]), 0.0)
        completion = datetime.now(UTC) + timedelta(hours=estimated_hours)
        return {
            "estimated_hours": round(estimated_hours, 2),
            "estimated_completion_date": completion.isoformat(),
            "confidence_interval_hours": [round(estimated_hours * 0.8, 2), round(estimated_hours * 1.2, 2)],
            "confidence": "high" if estimated_hours > 0 else "low",
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
        return {"status": payload.get("status", "trained"), "trained_at": payload.get("trained_at"), "metrics": payload.get("metrics"), "exists": True}
