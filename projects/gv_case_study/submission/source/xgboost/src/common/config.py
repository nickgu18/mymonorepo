from __future__ import annotations

import os
import re
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping

import yaml

from src.common.exceptions import ConfigurationError

_PLACEHOLDER_RE = re.compile(r"\$\{([^}]+)\}")
_DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "configs" / "base.yaml"


@dataclass(slots=True)
class ProjectConfig:
    root: Path


@dataclass(slots=True)
class RankingFiles:
    founder_experience: str
    education: str
    company_info: str


@dataclass(slots=True)
class TrainingFiles:
    founder_experience: str
    education: str
    company_info: str


@dataclass(slots=True)
class DataConfig:
    raw_dir: Path
    curated_dir: Path
    training_file: Path
    schema_version: str | None = None
    ranking_files: RankingFiles | None = None
    training_files: TrainingFiles | None = None


@dataclass(slots=True)
class FeatureConfig:
    registry: Path
    current_year: int = 2025
    selected_columns: list[str] = field(default_factory=list)
    target_column: str = ""


@dataclass(slots=True)
class ModelConfig:
    artifact_dir: Path
    algorithm: str
    hyperparameters: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TrackingConfig:
    uri: str
    experiment_name: str


@dataclass(slots=True)
class RegistryConfig:
    uri: Path
    model_path: Path

@dataclass(slots=True)
class LoggingConfig:
    level: str = "INFO"
    format: str = "json"


@dataclass(slots=True)
class Config:
    project: ProjectConfig
    data: DataConfig
    features: FeatureConfig
    model: ModelConfig
    tracking: TrackingConfig
    registry: RegistryConfig
    logging: LoggingConfig


def load_config(config_path: str | Path | None = None, env: str | None = None) -> Config:
    """Load YAML config, apply overrides, and materialize typed contracts."""

    path = Path(config_path).expanduser() if config_path else _DEFAULT_CONFIG
    if not path.exists():
        raise ConfigurationError(f"Config file not found: {path}")

    with path.open() as fh:
        config_data: MutableMapping[str, Any] = yaml.safe_load(fh) or {}

    if env:
        env_path = path.parent / f"{env}.yaml"
        if not env_path.exists():
            raise ConfigurationError(f"Env override '{env}' not found (expected {env_path})")
        with env_path.open() as fh:
            env_data = yaml.safe_load(fh) or {}
        config_data = _deep_update(config_data, env_data)

    expanded = _resolve_placeholders(config_data)
    return _materialize(expanded)


def _resolve_placeholders(raw: Mapping[str, Any]) -> Mapping[str, Any]:
    materialized: MutableMapping[str, Any] = deepcopy(raw)
    for _ in range(10):
        changed = _resolve_pass(materialized, materialized)
        if not changed:
            return materialized
    raise ConfigurationError("Exceeded placeholder resolution depth (possible circular reference)")


def _resolve_pass(node: Any, root: Mapping[str, Any]) -> bool:
    changed = False
    if isinstance(node, MutableMapping):
        for key, value in list(node.items()):
            if isinstance(value, str):
                expanded = _expand_string(value, root)
                if expanded != value:
                    node[key] = expanded
                    changed = True
            else:
                changed = _resolve_pass(value, root) or changed
    elif isinstance(node, list):
        for idx, value in enumerate(list(node)):
            if isinstance(value, str):
                expanded = _expand_string(value, root)
                if expanded != value:
                    node[idx] = expanded
                    changed = True
            else:
                changed = _resolve_pass(value, root) or changed
    return changed


def _expand_string(value: str, root: Mapping[str, Any]) -> str:
    expanded = os.path.expanduser(os.path.expandvars(value))

    def replace(match: re.Match[str]) -> str:
        reference = match.group(1).strip()
        return str(_dict_lookup(root, reference.split(".")))

    return _PLACEHOLDER_RE.sub(replace, expanded)


def _dict_lookup(data: Mapping[str, Any], keys: list[str]) -> Any:
    current: Any = data
    for key in keys:
        if isinstance(current, Mapping) and key in current:
            current = current[key]
        else:
            raise ConfigurationError(f"Unknown config reference: {'.'.join(keys)}")
    return current


def _materialize(data: Mapping[str, Any]) -> Config:
    project_root = Path(str(data["project"]["root"])).expanduser()

    def to_path(value: str | Path | None) -> Path:
        if value is None:
            raise ConfigurationError("Missing required path in config")
        path = Path(str(value)).expanduser()
        if not path.is_absolute():
            return (project_root / path).resolve()
        return path.resolve()

    project_cfg = ProjectConfig(root=project_root.resolve())

    ranking_cfg_raw = data["data"].get("ranking_files")
    training_cfg_raw = data["data"].get("training_files")
    if not ranking_cfg_raw:
        raise ConfigurationError("Missing 'data.ranking_files' mapping in config")
    if not training_cfg_raw:
        raise ConfigurationError("Missing 'data.training_files' mapping in config")
    try:
        ranking_cfg = RankingFiles(
            founder_experience=str(ranking_cfg_raw["founder_experience"]),
            education=str(ranking_cfg_raw["education"]),
            company_info=str(ranking_cfg_raw["company_info"]),
        )
        training_cfg = TrainingFiles(
            founder_experience=str(training_cfg_raw["founder_experience"]),
            education=str(training_cfg_raw["education"]),
            company_info=str(training_cfg_raw["company_info"]),
        )
    except KeyError as exc:  # pragma: no cover - config authoring error
        raise ConfigurationError(f"Missing ranking/training file key: {exc.args[0]}")

    data_cfg = DataConfig(
        raw_dir=to_path(data["data"]["raw_dir"]),
        curated_dir=to_path(data["data"]["curated_dir"]),
        training_file=to_path(data["data"]["training_file"]),
        schema_version=data["data"].get("schema_version"),
        ranking_files=ranking_cfg,
        training_files=training_cfg,
    )
    features_data = data["features"]
    if "target_column" not in features_data:
        raise ConfigurationError("Missing 'features.target_column' in config")
    target_column = features_data.get("target_column")
    if target_column in (None, ""):
        raise ConfigurationError("'features.target_column' must be set")
    if not features_data.get("selected_columns"):
        raise ConfigurationError("Missing 'features.selected_columns' in config")
    features_cfg = FeatureConfig(
        registry=to_path(features_data["registry"]),
        current_year=int(features_data.get("current_year", 2025)),
        selected_columns=list(features_data.get("selected_columns", [])),
        target_column=str(target_column),
    )
    model_cfg = ModelConfig(
        artifact_dir=to_path(data["model"]["artifact_dir"]),
        algorithm=str(data["model"].get("algorithm", "xgboost_ranker")),
        hyperparameters=dict(data["model"].get("hyperparameters", data["model"].get("params", {}))),
    )
    tracking_raw = data.get("tracking")
    if not tracking_raw:
        raise ConfigurationError("Missing 'tracking' section in config")
    if tracking_raw.get("uri") in (None, ""):
        raise ConfigurationError("Missing 'tracking.uri' in config")
    if tracking_raw.get("experiment_name") in (None, ""):
        raise ConfigurationError("Missing 'tracking.experiment_name' in config")
    tracking_cfg = TrackingConfig(
        uri=str(tracking_raw.get("uri")),
        experiment_name=str(tracking_raw.get("experiment_name")),
    )
    registry_cfg = RegistryConfig(
        uri=to_path(data["registry"]["uri"]),
        model_path=to_path(data["registry"]["model_path"]),
    )
    logging_cfg = LoggingConfig(
        level=str(data.get("logging", {}).get("level", "INFO")),
        format=str(data.get("logging", {}).get("format", "json")),
    )
    return Config(
        project=project_cfg,
        data=data_cfg,
        features=features_cfg,
        model=model_cfg,
        tracking=tracking_cfg,
        registry=registry_cfg,
        logging=logging_cfg,
    )


def _deep_update(base: MutableMapping[str, Any], overrides: Mapping[str, Any]) -> MutableMapping[str, Any]:
    result = deepcopy(base)
    for key, value in overrides.items():
        if key in result and isinstance(result[key], MutableMapping) and isinstance(value, Mapping):
            result[key] = _deep_update(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result
