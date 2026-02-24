from __future__ import annotations

from pathlib import Path

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.config import load_config
from src.data.loaders import clean, load_raw
from src.features.pipeline import FeaturePipeline
from src.features.feature_factory import build_post_split_feature_frames
from src.features.types import FeatureMatrix, FeatureMetadata
from src.features.pipeline import _to_bool_series
from src.models.io import load_model_bundle
from src.predict.inference import predict_batch


def _latest_notebook_run_dir(artifact_dir: Path) -> Path:
    runs_root = artifact_dir / "notebook_runs"
    run_dirs = sorted([p for p in runs_root.iterdir() if p.is_dir()])
    if not run_dirs:
        raise AssertionError(f"No notebook_runs found under {runs_root}")
    return run_dirs[-1]


def test_predict_batch_matches_model_feature_columns() -> None:
    """End-to-end check that ranking features match model feature_columns."""

    cfg = load_config()
    run_dir = _latest_notebook_run_dir(cfg.model.artifact_dir)

    bundle = load_model_bundle(
        registry_cfg=cfg.registry,
        project_root=cfg.project.root,
        model_root=run_dir,
    )

    raw_ranking = load_raw(cfg.data, dataset="ranking")
    clean_ranking = clean(raw_ranking)

    # Base pre-split founder features (label-agnostic).
    feature_pipeline = FeaturePipeline(cfg.features)
    base_fm = feature_pipeline.build_matrix(clean_ranking)
    base_frame = base_fm.frame.copy()

    # Build post-snapshot aggregates for inference using full history up to current_year.
    exp = clean_ranking.experience.copy()
    exp["is_founder"] = _to_bool_series(exp["is_founder"])
    founder_history = exp[exp["is_founder"] == True].copy()  # noqa: E712
    founder_ids = base_frame["person_id"].astype(str).unique().tolist()

    perf_agg, network_df, team_df = build_post_split_feature_frames(
        experience=exp,
        founder_history=founder_history,
        education=clean_ranking.education.copy(),
        company_info=clean_ranking.company_info.copy(),
        founder_ids=founder_ids,
        current_year=cfg.features.current_year,
    )

    enriched = base_frame.merge(perf_agg, on="person_id", how="left")
    enriched = enriched.merge(network_df, on="person_id", how="left")
    enriched = enriched.merge(team_df, on="company_id", how="left")

    ranking_features = FeatureMatrix(
        frame=enriched,
        metadata=FeatureMetadata(
            feature_columns=bundle.feature_columns,
            entity_column="person_id",
        ),
    )

    preds = predict_batch(bundle, ranking_features, shap_top_n=1)

    assert not preds.empty
    assert "score" in preds.columns
    assert "rank" in preds.columns
