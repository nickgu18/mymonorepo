from __future__ import annotations

from pathlib import Path

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.config import load_config
from src.data.loaders import clean, load_raw
from src.features.pipeline import FeaturePipeline


def test_feature_pipeline_founder_matrix_matches_xgboost_process_step3() -> None:
    """Ensure FeaturePipeline.build_matrix aligns with xgboost_process step 3."""

    cfg = load_config()
    raw_training = load_raw(cfg.data, dataset="training")
    clean_training = clean(raw_training)

    fp = FeaturePipeline(cfg.features)
    fm = fp.build_matrix(clean_training)
    frame = fm.frame

    # Step 3.2.1–3.2.3.1: one row per founder (4,772) with last founded company.
    assert frame.shape[0] == 4772
    assert frame["person_id"].nunique() == 4772

    # Core columns required by the xgboost_process spec for the
    # initial (pre-split) founder snapshot.
    expected_cols = [
        "person_id",
        "company_id",
        "performance",
        "education_tier",
        "education_level_score",
        "industry",
    ]
    for col in expected_cols:
        assert col in frame.columns
