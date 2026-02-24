from __future__ import annotations

from collections import defaultdict, deque
from typing import Mapping, Tuple, Optional, List

import pandas as pd


def compute_team_size(
    founder_history: pd.DataFrame,
    cut_off_years: Optional[Mapping[str, int]] = None,
) -> dict:
    """Count founders per company based on founder_history.

    When cut_off_years is provided, it is interpreted as a mapping from
    company_id -> cut-off year (inclusive). Only founder rows whose
    start_date year is <= that company's cut-off year are counted. This
    keeps team sizes time-respecting for label-company snapshots.
    """

    if founder_history.empty:
        return {}

    work = founder_history.loc[founder_history["is_founder"] == True].copy()  # noqa: E712
    if work.empty:
        return {}

    if cut_off_years is not None:
        work["company_id"] = work["company_id"].astype(str)
        work["start_date"] = pd.to_datetime(work.get("start_date"), errors="coerce")
        work["cut_off_year"] = work["company_id"].map(dict(cut_off_years))
        mask = work["cut_off_year"].isna()
        has_start = work["start_date"].notna()
        mask |= has_start & (work["start_date"].dt.year <= work["cut_off_year"])
        work = work[mask].copy()
        if work.empty:
            return {}

    return (
        work.groupby("company_id")["person_id"]
        .nunique()
        .to_dict()
    )


def compute_network_features(
    experience: pd.DataFrame,
    founder_ids: list,
    edu_tier_lookup: Mapping[str, float],
    current_year: int,
    cut_off_years: Optional[Mapping[str, int]] = None,
) -> Tuple[dict, dict, dict]:
    """Build adjacency and derive network features for founders."""

    adjacency = build_co_worker_adjacency(
        experience,
        current_year=current_year,
        cut_off_years=cut_off_years,
    )
    for founder_id in founder_ids:
        adjacency.setdefault(founder_id, set())
    component_sizes = _component_sizes(adjacency)
    network_quality_map = _network_quality(adjacency, edu_tier_lookup)
    return adjacency, component_sizes, network_quality_map


def build_co_worker_adjacency(
    experience: pd.DataFrame,
    current_year: int,
    cut_off_years: Optional[Mapping[str, int]] = None,
) -> dict[str, set[str]]:
    """Construct co-worker graph from experience data.

    When cut_off_years is provided, it is interpreted as a mapping from
    person_id -> cut-off year (inclusive). For each person, only tenure
    up to the end of the cut-off year is considered when building
    overlaps, which keeps network features aligned with a snapshot date.
    """

    adjacency: dict[str, set[str]] = defaultdict(set)
    relevant = experience.dropna(subset=["company_id", "person_id", "start_date"]).copy()
    if relevant.empty:
        return adjacency

    fallback_end = pd.Timestamp(current_year, 12, 31)
    if "end_date" not in relevant.columns:
        relevant["end_date"] = pd.NaT

    relevant["start_date"] = pd.to_datetime(relevant["start_date"], errors="coerce")
    relevant["end_date"] = pd.to_datetime(relevant["end_date"], errors="coerce")

    cut_off_years_dict = dict(cut_off_years or {})

    for _, group in relevant.groupby("company_id"):
        collapsed = (
            group.groupby("person_id")
            .agg(start_date=("start_date", "min"), end_date=("end_date", "max"))
            .dropna(subset=["start_date"])
            .reset_index()
        )
        if collapsed.empty:
            continue
        intervals = []
        for row in collapsed.itertuples(index=False):
            person_id = str(row.person_id)
            start_date = row.start_date
            end_date = row.end_date if pd.notna(row.end_date) else fallback_end

            if cut_off_years_dict:
                cut_year = cut_off_years_dict.get(person_id)
                if cut_year is not None:
                    cut_end = pd.Timestamp(int(cut_year), 12, 31)
                    if start_date > cut_end:
                        # Entire tenure is after the snapshot; skip.
                        continue
                    if end_date > cut_end:
                        end_date = cut_end

            intervals.append((person_id, start_date, end_date))

        for idx in range(len(intervals)):
            person_id, start_i, end_i = intervals[idx]
            adjacency.setdefault(person_id, set())
            for jdx in range(idx + 1, len(intervals)):
                other_id, start_j, end_j = intervals[jdx]
                adjacency.setdefault(other_id, set())
                if _intervals_overlap(start_i, end_i, start_j, end_j):
                    adjacency[person_id].add(other_id)
                    adjacency[other_id].add(person_id)
    return adjacency


def compute_founder_performance_aggregates(
    founder_history: pd.DataFrame,
    perf_lookup: Mapping[str, float],
    cut_off_years: Optional[Mapping[str, int]] = None,
) -> pd.DataFrame:
    """Aggregate company performance history into founder-level features.

    Expects founder_history to contain only rows where the person is a founder.

    When cut_off_years is provided, it is interpreted as a mapping from
    person_id -> cut-off year (inclusive). Only company histories with
    start_date year <= that cut-off year are considered for each
    founder, keeping aggregates time-respecting.
    """

    rows: list[dict] = []
    if founder_history.empty:
        return pd.DataFrame(
            columns=[
                "person_id",
                "founder_has_perf",
                "founder_perf_mean",
                "founder_perf_max",
                "founder_perf_last",
            ]
        )

    work = founder_history.copy()
    work["company_id"] = work["company_id"].astype(str)
    work["start_date"] = pd.to_datetime(work.get("start_date"), errors="coerce")

    cut_off_years_dict = dict(cut_off_years or {})

    for person_id, history in work.groupby("person_id"):
        cut_year = cut_off_years_dict.get(str(person_id))
        if cut_year is not None:
            start_year = history["start_date"].dt.year
            history = history[start_year <= int(cut_year)]

        if history.empty:
            rows.append(
                {
                    "person_id": person_id,
                    "founder_has_perf": 0,
                    "founder_perf_mean": float("nan"),
                    "founder_perf_max": float("nan"),
                    "founder_perf_last": float("nan"),
                }
            )
            continue

        company_ids = history["company_id"].dropna().astype(str).tolist()
        perfs = [perf_lookup.get(cid) for cid in company_ids]
        vals = [float(p) for p in perfs if p is not None and not pd.isna(p)]

        founder_has_perf = int(len(vals) > 0)
        founder_perf_mean = float(sum(vals) / len(vals)) if vals else float("nan")
        founder_perf_max = float(max(vals)) if vals else float("nan")

        # Last performance: prefer performance of the last founded company
        # (by `order`), otherwise fall back to the last available value.
        last_perf_val = float("nan")
        if not history.empty and "order" in history.columns:
            last_company = history.sort_values("order").iloc[-1]["company_id"]
            if pd.notna(last_company):
                last_perf_val = perf_lookup.get(str(last_company))
        if last_perf_val is None or (isinstance(last_perf_val, float) and pd.isna(last_perf_val)):
            last_perf_val = vals[-1] if vals else float("nan")
        founder_perf_last = float(last_perf_val) if not pd.isna(last_perf_val) else float("nan")

        rows.append(
            {
                "person_id": person_id,
                "founder_has_perf": founder_has_perf,
                "founder_perf_mean": founder_perf_mean,
                "founder_perf_max": founder_perf_max,
                "founder_perf_last": founder_perf_last,
            }
        )

    return pd.DataFrame(rows)


def build_post_split_feature_frames(
    experience: pd.DataFrame,
    founder_history: pd.DataFrame,
    education: pd.DataFrame,
    company_info: pd.DataFrame,
    founder_ids: List[str],
    current_year: int,
    founder_cutoff_years: Optional[Mapping[str, int]] = None,
    company_cutoff_years: Optional[Mapping[str, int]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build post-split, time-respecting aggregates for founders.

    This helper centralizes the notebook logic used in Phase 5 of the
    GV exercise notebook so both training and inference can attach the
    same derived features:

    - founder-level performance aggregates
    - first-degree network size and quality
    - team size per company

    Args:
        experience: Full experience table (all roles).
        founder_history: Experience rows where the person is a founder.
        education: Education table with at least education_tier.
        company_info: Company info table with performance.
        founder_ids: Founder person_ids to score.
        current_year: Fallback year for open-ended tenures.
        founder_cutoff_years: Optional mapping person_id -> cut-off year.
        company_cutoff_years: Optional mapping company_id -> cut-off year.

    Returns:
        Tuple of (perf_agg, network_df, team_df).
    """

    # 1) Founder performance aggregates.
    perf_lookup: dict[str, float] = {}
    if not company_info.empty and "company_id" in company_info.columns and "performance" in company_info.columns:
        perf_lookup = (
            company_info.assign(company_id=company_info["company_id"].astype(str))
            .set_index("company_id")["performance"]
            .to_dict()
        )

    perf_agg = compute_founder_performance_aggregates(
        founder_history,
        perf_lookup,
        cut_off_years=founder_cutoff_years,
    )

    # 2) Network features using co-worker graph.
    edu_tier_lookup: dict[str, float] = {}
    if not education.empty and "person_id" in education.columns and "education_tier" in education.columns:
        edu_tier_lookup = (
            education.assign(person_id=education["person_id"].astype(str))
            .set_index("person_id")["education_tier"]
            .astype(float)
            .to_dict()
        )

    founder_ids_str = [str(pid) for pid in founder_ids]
    adjacency, _component_sizes, network_quality = compute_network_features(
        experience=experience,
        founder_ids=founder_ids_str,
        edu_tier_lookup=edu_tier_lookup,
        current_year=current_year,
        cut_off_years=founder_cutoff_years,
    )

    network_rows: list[dict[str, object]] = []
    for pid in founder_ids_str:
        neighbors = adjacency.get(pid, set())
        network_rows.append(
            {
                "person_id": pid,
                "network_size_1st": len(neighbors),
                "network_quality_1st": float(network_quality.get(pid, 0.0)),
            }
        )
    network_df = pd.DataFrame(network_rows)

    # 3) Team size per company based on founder history.
    team_size_map = compute_team_size(
        founder_history,
        cut_off_years=company_cutoff_years,
    )
    team_rows: list[dict[str, object]] = [
        {"company_id": str(cid), "team_size": int(size)} for cid, size in team_size_map.items()
    ]
    team_df = (
        pd.DataFrame(team_rows)
        if team_rows
        else pd.DataFrame(columns=["company_id", "team_size"])
    )

    return perf_agg, network_df, team_df


def _intervals_overlap(
    start_a: pd.Timestamp,
    end_a: pd.Timestamp,
    start_b: pd.Timestamp,
    end_b: pd.Timestamp,
) -> bool:
    return bool(start_a <= end_b and start_b <= end_a)


def _component_sizes(adjacency: Mapping[str, set[str]]) -> dict[str, int]:
    sizes: dict[str, int] = {}
    visited: set[str] = set()
    for node in adjacency.keys():
        if node in visited:
            continue
        stack = deque([node])
        component: set[str] = set()
        while stack:
            current = stack.pop()
            if current in component:
                continue
            component.add(current)
            for neighbor in adjacency.get(current, set()):
                if neighbor not in component:
                    stack.append(neighbor)
        for member in component:
            sizes[member] = max(len(component) - 1, 0)
        visited.update(component)
    return sizes


def _network_quality(adjacency: Mapping[str, set[str]], edu_lookup: Mapping[str, float]) -> dict[str, float]:
    quality: dict[str, float] = {}
    for person_id, neighbors in adjacency.items():
        if not neighbors:
            quality[person_id] = 0.0
            continue
        tiers = [float(edu_lookup.get(neighbor, 0.0)) for neighbor in neighbors]
        kept = [value for value in tiers if not pd.isna(value) and value > 0]
        quality[person_id] = float(sum(kept) / len(kept)) if kept else 0.0
    return quality


__all__ = [
    "compute_team_size",
    "compute_network_features",
    "build_co_worker_adjacency",
    "compute_founder_performance_aggregates",
    "build_post_split_feature_frames",
]
