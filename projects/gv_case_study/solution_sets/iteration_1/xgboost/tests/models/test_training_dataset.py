from __future__ import annotations

from pathlib import Path

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.config import load_config
from src.data.loaders import clean, load_raw, load_targets
from src.models.training_pipeline import build_training_dataset


def test_build_training_dataset_matches_xgboost_process_step_3_2() -> None:
    cfg = load_config()

    raw_training = load_raw(cfg.data, dataset="training")
    raw_ranking = load_raw(cfg.data, dataset="ranking")
    clean_training = clean(raw_training)
    clean_ranking = clean(raw_ranking)
    targets = load_targets(cfg.data)

    train_df = build_training_dataset(clean_training, clean_ranking, targets, cfg.features)

    # After attaching targets and removing leakage, we expect 4,769 founders.
    assert train_df.shape[0] == 4769

    # Training frame should contain IDs, metadata, simplified features, and label.
    expected_cols = [
        "person_id",
        "company_id",
        "industry",
        "company_founded",
        cfg.features.target_column,
        "performance",
        "education_tier",
        "education_level_score",
        "founder_has_perf",
        "founder_perf_mean",
        "founder_perf_max",
        "founder_perf_last",
    ]
    for col in expected_cols:
        assert col in train_df.columns

