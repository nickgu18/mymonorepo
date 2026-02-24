from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

import xgboost as xgb

from src.common import RegistryConfig
from src.common.exceptions import ModelLoadError
from src.models.types import ModelBundle


def load_model_bundle(
    registry_cfg: RegistryConfig,
    project_root: Path,
    model_root: Path | None = None,
) -> ModelBundle:
    """Load the trained ranker and supporting metadata."""

    for model_path, artifacts_path in _candidate_artifact_pairs(registry_cfg, project_root, model_root):
        if model_path.exists() and artifacts_path.exists():
            with artifacts_path.open() as fh:
                artifacts = json.load(fh)
            estimator = xgb.XGBRanker()
            estimator.load_model(model_path)
            feature_columns = artifacts.get("feature_columns")
            outcome_lookup = artifacts.get("outcome_lookup") or {}
            if not feature_columns:
                raise ModelLoadError(
                    artifact_path=str(artifacts_path),
                    message="Artifacts missing required keys (feature_columns)",
                )
            return ModelBundle(
                estimator=estimator,
                feature_columns=list(feature_columns),
                outcome_lookup=outcome_lookup,
            )

    searched = ", ".join(str(pair[0].parent) for pair in _candidate_artifact_pairs(registry_cfg, project_root, model_root))
    raise ModelLoadError(artifact_path=searched, message="Model or artifacts not found")


def _candidate_artifact_pairs(
    registry_cfg: RegistryConfig,
    project_root: Path,
    model_root: Path | None,
) -> Tuple[Tuple[Path, Path], ...]:
    """Return ordered search paths for (model, artifacts)."""

    candidates: list[Tuple[Path, Path]] = []
    if model_root:
        candidates.append((model_root / "ranker.json", model_root / "artifacts.json"))
    candidates.append((registry_cfg.model_path, registry_cfg.uri))

    registry_dir = registry_cfg.model_path.parent
    candidates.append((registry_dir / "ranker.json", registry_dir / "artifacts.json"))

    if registry_dir.exists():
        timestamped = sorted([p for p in registry_dir.iterdir() if p.is_dir()], reverse=True)
        for run_dir in timestamped:
            candidates.append((run_dir / "ranker.json", run_dir / "artifacts.json"))

    experiments_dir = project_root / "experiments"
    candidates.append((experiments_dir / "models" / "ranker.json", experiments_dir / "models" / "artifacts.json"))
    candidates.append((experiments_dir / "initial" / "models" / "ranker.json", experiments_dir / "initial" / "models" / "artifacts.json"))

    # Remove duplicates while keeping order
    unique: list[Tuple[Path, Path]] = []
    seen: set[Tuple[Path, Path]] = set()
    for pair in candidates:
        normalized = (pair[0].resolve(), pair[1].resolve())
        if normalized not in seen:
            seen.add(normalized)
            unique.append(pair)
    return tuple(unique)
