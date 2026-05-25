from __future__ import annotations

import json
import os
from typing import Dict, Any

REGISTRY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'registry.json'))
os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)


def _load_registry() -> Dict[str, Any]:
    if not os.path.exists(REGISTRY_PATH):
        return {}
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def _save_registry(reg: Dict[str, Any]):
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(reg, f, indent=2)


def register_model(name: str, version: str, path: str, metrics: Dict[str, Any]):
    reg = _load_registry()
    reg[name] = {
        'version': version,
        'path': path,
        'metrics': metrics,
    }
    _save_registry(reg)


def get_model_entry(name: str):
    reg = _load_registry()
    return reg.get(name)
"""Persistent model registry for trained artifacts."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

@dataclass
class ModelArtifact:
    name: str
    version: str
    path: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    cross_validation: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ModelRegistry:
    def __init__(self) -> None:
        self.registry_path = Path(settings.MODEL_DIR) / "predictions" / "registry.json"
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._models: dict[str, ModelArtifact] = {}
        self._load()

    def _load(self) -> None:
        if not self.registry_path.exists():
            return
        data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        for name, payload in data.items():
            version = payload.get("model_version", "v1")
            self._models[f"{name}:{version}"] = ModelArtifact(
                name=name,
                version=version,
                path=payload.get("path"),
                metrics=payload.get("metrics", {}),
                cross_validation=payload.get("cross_validation", {}),
                created_at=datetime.fromisoformat(payload.get("trained_at")) if payload.get("trained_at") else datetime.now(timezone.utc),
            )

    def _persist(self) -> None:
        serializable = {
            key: {
                "model_version": artifact.version,
                "path": artifact.path,
                "metrics": artifact.metrics,
                "cross_validation": artifact.cross_validation,
                "trained_at": artifact.created_at.isoformat(),
            }
            for key, artifact in self._models.items()
        }
        self.registry_path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")

    def register(self, artifact: ModelArtifact) -> None:
        self._models[f"{artifact.name}:{artifact.version}"] = artifact
        self._persist()

    def get(self, name: str, version: str) -> ModelArtifact | None:
        return self._models.get(f"{name}:{version}")

    def latest(self, name: str) -> ModelArtifact | None:
        candidates = [artifact for key, artifact in self._models.items() if key.startswith(f"{name}:")]
        if not candidates:
            return None
        return sorted(candidates, key=lambda artifact: artifact.created_at, reverse=True)[0]
