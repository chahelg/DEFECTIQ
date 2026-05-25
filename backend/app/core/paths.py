"""Filesystem helpers for app-wide resources."""

from __future__ import annotations

from pathlib import Path

from app.core.config import settings


REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "backend"


def get_ml_models_dir() -> Path:
    path = REPO_ROOT / settings.ML_MODELS_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path
