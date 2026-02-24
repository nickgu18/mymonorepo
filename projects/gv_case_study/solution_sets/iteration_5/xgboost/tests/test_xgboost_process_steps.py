from __future__ import annotations

from pathlib import Path
from typing import Tuple

import math
import pandas as pd

# Ensure the project src/ directory is importable as the `src` package
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.config import load_config
from src.data.loaders import clean, load_raw, load_targets
from src.features.feature_factory import compute_founder_performance_aggregates
from src.features.pipeline import _to_bool_series
from src.models.metrics import calculate_relevance_grade


def _load_clean_training() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load and clean the three curated training tables."""

    cfg = load_config()
    raw_training = load_raw(cfg.data, dataset="training")
    clean_training = clean(raw_training)
    return (
        clean_training.experience.copy(),
        clean_training.education.copy(),
        clean_training.company_info.copy(),
    )


def _load_clean_inference() -> pd.DataFrame:
    cfg = load_config()
    raw_ranking = load_raw(cfg.data, dataset="ranking")
    clean_ranking = clean(raw_ranking)
    return clean_ranking.experience.copy()


def _build_last_founded_company_frame(experience: pd.DataFrame) -> pd.DataFrame:
    """Step 3.2.1 – last founded company per founder."""

    exp = experience.copy()
    if "is_founder" not in exp.columns:
        raise AssertionError("expected is_founder column in founder_experience")

    exp["is_founder"] = _to_bool_series(exp["is_founder"])
    founder_rows = exp[exp["is_founder"] == True].copy()  # noqa: E712
    # The order column is already a string with leading zeros; lexicographic
    # sorting matches chronological order.
    founder_rows = founder_rows.sort_values(["person_id", "order"])
    last_rows = founder_rows.groupby("person_id", as_index=False).tail(1)
    return last_rows


def _attach_education(last_rows: pd.DataFrame, education: pd.DataFrame) -> pd.DataFrame:
    """Step 3.2.2 – attach education_training."""

    return last_rows.merge(education, on="person_id", how="left")


def _attach_company_info_and_perf_features(
    last_with_edu: pd.DataFrame,
    experience: pd.DataFrame,
    company_info: pd.DataFrame,
) -> pd.DataFrame:
    """Steps 3.2.3 + 3.2.3.1 – company_info + perf aggregates."""

    base = last_with_edu.merge(company_info, on="company_id", how="left")

    perf_lookup = company_info.set_index("company_id")["performance"].to_dict()

    # Restrict to founders only for aggregates.
    exp = experience.copy()
    exp["is_founder"] = _to_bool_series(exp["is_founder"])
    founder_history = exp[exp["is_founder"] == True].copy()  # noqa: E712

    agg = compute_founder_performance_aggregates(founder_history, perf_lookup)
    return base.merge(agg, on="person_id", how="left")


def test_step_3_2_1_last_company_shape_and_columns() -> None:
    experience, _, _ = _load_clean_training()

    last_rows = _build_last_founded_company_frame(experience)

    assert last_rows.shape == (4772, 12)
    assert list(last_rows.columns) == [
        "person_id",
        "order",
        "company_id",
        "title",
        "job_type",
        "start_date",
        "end_date",
        "is_c_suite",
        "is_employee",
        "is_executive",
        "is_founder",
        "is_on_board",
    ]


def test_step_3_2_2_attach_education_shape_and_columns() -> None:
    experience, education, _ = _load_clean_training()

    last_rows = _build_last_founded_company_frame(experience)
    combined = _attach_education(last_rows, education)

    assert combined.shape == (4772, 14)
    assert "education_tier" in combined.columns
    assert "highest_level" in combined.columns


def test_step_3_2_3_perf_features_shape_and_columns() -> None:
    experience, education, company_info = _load_clean_training()

    last_rows = _build_last_founded_company_frame(experience)
    last_with_edu = _attach_education(last_rows, education)
    with_perf = _attach_company_info_and_perf_features(last_with_edu, experience, company_info)

    # Doc comment says (4772, 19) but the natural schema here is:
    # 12 (experience) + 2 (education) + 2 (company_info: industry, performance)
    # + 4 (perf aggregates) = 20 columns.
    assert with_perf.shape == (4772, 20)
    for col in [
        "industry",
        "performance",
        "founder_has_perf",
        "founder_perf_mean",
        "founder_perf_max",
        "founder_perf_last",
    ]:
        assert col in with_perf.columns
