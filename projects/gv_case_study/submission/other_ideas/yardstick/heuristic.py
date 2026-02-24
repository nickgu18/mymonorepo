from __future__ import annotations

import math
from typing import Tuple

import numpy as np
import pandas as pd


def _safe_fill_numeric(series: pd.Series, fill: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(fill)


def _normalize(series: pd.Series, denom_floor: float = 1.0) -> pd.Series:
    values = _safe_fill_numeric(series, 0.0)
    denom = max(float(values.max()), denom_floor)
    return values.astype(float) / denom


def build_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["norm_edu_tier"] = _normalize(out.get("education_tier", 0.0))
    out["norm_edu_level"] = _normalize(out.get("education_level_score", 0.0))
    out["basic_subscore"] = 0.5 * out["norm_edu_tier"] + 0.5 * out["norm_edu_level"]
    return out[["person_id", "basic_subscore"]]


def build_experience_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    founder_flag = out.get("is_founder_of_target")
    if founder_flag is None:
        founder_flag = pd.Series(False, index=out.index)
    founder_flag = founder_flag.fillna(False).astype(bool)
    out["norm_team_size"] = _normalize(out.get("team_size", 0.0))
    out["experience_subscore"] = 0.6 * founder_flag.astype(float) + 0.4 * out["norm_team_size"]
    return out[["person_id", "experience_subscore"]]


def build_performance_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    has_perf = out.get("founder_has_perf")
    if has_perf is None:
        has_perf = pd.Series(0.0, index=out.index)
    has_perf = _safe_fill_numeric(has_perf, 0.0).clip(0.0, 1.0)
    out["norm_perf_mean"] = _normalize(out.get("founder_perf_mean", 0.0))
    out["norm_perf_max"] = _normalize(out.get("founder_perf_max", 0.0))
    out["norm_perf_last"] = _normalize(out.get("founder_perf_last", 0.0))
    out["performance_subscore"] = (
        0.2 * has_perf + 0.4 * out["norm_perf_max"] + 0.25 * out["norm_perf_mean"] + 0.15 * out["norm_perf_last"]
    )
    return out[["person_id", "performance_subscore"]]


def build_network_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["norm_network_quality"] = _normalize(out.get("network_quality_1st", 0.0))
    out["norm_network_size"] = _normalize(out.get("network_size_1st", 0.0))
    out["network_subscore"] = 0.7 * out["norm_network_quality"] + 0.3 * out["norm_network_size"]
    return out[["person_id", "network_subscore"]]


def build_company_features(df: pd.DataFrame, enabled: bool = True) -> pd.DataFrame:
    out = df.copy()
    if not enabled:
        out["company_subscore"] = 0.0
        return out[["person_id", "company_subscore"]]
    out["norm_company_perf"] = _normalize(out.get("performance", 0.0))
    out["company_subscore"] = out["norm_company_perf"]
    return out[["person_id", "company_subscore"]]


def compute_heuristic_score(df: pd.DataFrame, use_company: bool = True) -> pd.DataFrame:
    base = df.copy()
    b = build_basic_features(base)
    e = build_experience_features(base)
    p = build_performance_features(base)
    n = build_network_features(base)
    c = build_company_features(base, enabled=use_company)
    merged = base[["person_id"]].merge(b, on="person_id", how="left").merge(e, on="person_id", how="left").merge(p, on="person_id", how="left").merge(n, on="person_id", how="left").merge(c, on="person_id", how="left")
    if use_company:
        merged["heuristic_score"] = (
            0.30 * merged["performance_subscore"]
            + 0.25 * merged["network_subscore"]
            + 0.25 * merged["basic_subscore"]
            + 0.15 * merged["experience_subscore"]
            + 0.05 * merged["company_subscore"]
        )
    else:
        merged["heuristic_score"] = (
            0.35 * merged["performance_subscore"]
            + 0.30 * merged["network_subscore"]
            + 0.20 * merged["basic_subscore"]
            + 0.15 * merged["experience_subscore"]
        )
    return merged