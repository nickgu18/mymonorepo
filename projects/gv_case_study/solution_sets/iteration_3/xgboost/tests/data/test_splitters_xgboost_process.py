from __future__ import annotations

from pathlib import Path

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.config import load_config
from src.data.loaders import clean, load_raw, load_targets
from src.data.splitters import split_by_industry
from src.models.training_pipeline import build_training_dataset


def test_split_by_industry_temporal_and_per_industry() -> None:
    cfg = load_config()

    # Build the full training dataset (Step 3 completed).
    raw_training = load_raw(cfg.data, dataset="training")
    raw_ranking = load_raw(cfg.data, dataset="ranking")
    clean_training = clean(raw_training)
    clean_ranking = clean(raw_ranking)
    targets = load_targets(cfg.data)

    train_df_full = build_training_dataset(clean_training, clean_ranking, targets, cfg.features)

    feature_cols = cfg.features.selected_columns
    target_col = cfg.features.target_column

    (
        X_train,
        y_train,
        X_test,
        y_test,
        train_df,
        test_df,
        train_groups,
        test_groups,
        industry_names,
    ) = split_by_industry(train_df_full, feature_cols, target_col=target_col, train_ratio=0.8)

    # Basic sanity: all splits are non-empty.
    assert not train_df.empty
    assert not test_df.empty
    assert len(X_train) == len(y_train) == len(train_df)
    assert len(X_test) == len(y_test) == len(test_df)

    # Per-industry temporal split: within each industry, the newest training
    # company_founded must be no later than the oldest test company_founded.
    for industry in industry_names:
        train_cohort = train_df[train_df["industry"] == industry]
        test_cohort = test_df[test_df["industry"] == industry]
        if train_cohort.empty or test_cohort.empty:
            continue
        assert train_cohort["company_founded"].max() <= test_cohort["company_founded"].min()

    # Group sizes match the returned DataFrames.
    assert sum(train_groups) == len(train_df)
    assert sum(test_groups) == len(test_df)

