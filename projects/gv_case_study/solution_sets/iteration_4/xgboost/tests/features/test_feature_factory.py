from __future__ import annotations

from pathlib import Path

import pandas as pd

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.common.config import load_config
from src.data.loaders import clean, load_raw
from src.features.feature_factory import (
    build_co_worker_adjacency,
    compute_network_features,
    compute_team_size,
    build_post_split_feature_frames,
)
from src.features.pipeline import _to_bool_series


def test_feature_factory_team_size_and_network_on_real_data() -> None:
    cfg = load_config()
    raw_training = load_raw(cfg.data, dataset="training")
    clean_training = clean(raw_training)

    exp = clean_training.experience.copy()
    exp["is_founder"] = _to_bool_series(exp["is_founder"])
    founder_history = exp[exp["is_founder"] == True].copy()  # noqa: E712
    founder_ids = (
        founder_history["person_id"].dropna().astype(str).unique().tolist()
    )

    # Team sizes should exist for companies that have at least one founder.
    team_size_map = compute_team_size(founder_history)
    assert len(team_size_map) > 0
    assert all(size >= 1 for size in team_size_map.values())

    # Network features should be defined for all founder_ids.
    edu = clean_training.education.copy()
    edu_tier_lookup = (
        edu.set_index("person_id")["education_tier"].astype(float).to_dict()
    )
    adjacency, component_sizes, network_quality_map = compute_network_features(
        exp, founder_ids, edu_tier_lookup, current_year=cfg.features.current_year
    )

    assert set(founder_ids).issubset(set(adjacency.keys()))
    assert set(founder_ids).issubset(set(component_sizes.keys()))
    assert set(founder_ids).issubset(set(network_quality_map.keys()))

    # Basic sanity on network outputs.
    assert all(size >= 0 for size in component_sizes.values())
    assert all(value >= 0.0 for value in network_quality_map.values())


def test_build_co_worker_adjacency_tiny_example() -> None:
    data = [
        # company A: p1 and p2 overlap, p3 non-overlap
        ("p1", "A", "2020-01-01", "2020-12-31"),
        ("p2", "A", "2020-06-01", "2020-12-31"),
        ("p3", "A", "2021-01-01", "2021-12-31"),
        # company B: p2 and p3 overlap
        ("p2", "B", "2021-01-01", "2021-12-31"),
        ("p3", "B", "2021-06-01", "2021-12-31"),
    ]
    df = pd.DataFrame(data, columns=["person_id", "company_id", "start_date", "end_date"])
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    adjacency = build_co_worker_adjacency(df, current_year=2025)

    assert adjacency["p1"] == {"p2"}
    assert adjacency["p2"] == {"p1", "p3"}
    assert adjacency["p3"] == {"p2"}


def test_build_post_split_feature_frames_inference_like() -> None:
    cfg = load_config()
    raw_ranking = load_raw(cfg.data, dataset="ranking")
    clean_ranking = clean(raw_ranking)

    exp = clean_ranking.experience.copy()
    exp["is_founder"] = _to_bool_series(exp["is_founder"])
    founder_history = exp[exp["is_founder"] == True].copy()  # noqa: E712
    founder_ids = founder_history["person_id"].dropna().astype(str).unique().tolist()

    perf_agg, network_df, team_df = build_post_split_feature_frames(
        experience=exp,
        founder_history=founder_history,
        education=clean_ranking.education.copy(),
        company_info=clean_ranking.company_info.copy(),
        founder_ids=founder_ids,
        current_year=cfg.features.current_year,
    )

    assert not perf_agg.empty
    assert not network_df.empty
    assert not team_df.empty

    for col in [
        "person_id",
        "founder_has_perf",
        "founder_perf_mean",
        "founder_perf_max",
        "founder_perf_last",
    ]:
        assert col in perf_agg.columns

    for col in [
        "person_id",
        "network_size_1st",
        "network_quality_1st",
    ]:
        assert col in network_df.columns

    for col in [
        "company_id",
        "team_size",
    ]:
        assert col in team_df.columns
