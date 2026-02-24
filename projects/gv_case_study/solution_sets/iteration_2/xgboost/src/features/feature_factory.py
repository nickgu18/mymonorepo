from __future__ import annotations

from collections import defaultdict, deque
from typing import Mapping, Tuple

import pandas as pd


def compute_team_size(founder_history: pd.DataFrame) -> dict:
    """Count founders per company based on founder_history."""

    return (
        founder_history.loc[founder_history["is_founder"] == True]  # noqa: E712
        .groupby("company_id")["person_id"]
        .nunique()
        .to_dict()
    )


def compute_network_features(
    experience: pd.DataFrame,
    founder_ids: list,
    edu_tier_lookup: Mapping[str, float],
    current_year: int,
) -> Tuple[dict, dict, dict]:
    """Build adjacency and derive network features for founders."""

    adjacency = build_co_worker_adjacency(experience, current_year=current_year)
    for founder_id in founder_ids:
        adjacency.setdefault(founder_id, set())
    component_sizes = _component_sizes(adjacency)
    network_quality_map = _network_quality(adjacency, edu_tier_lookup)
    return adjacency, component_sizes, network_quality_map


def build_co_worker_adjacency(experience: pd.DataFrame, current_year: int) -> dict[str, set[str]]:
    """Construct co-worker graph from experience data."""

    adjacency: dict[str, set[str]] = defaultdict(set)
    relevant = experience.dropna(subset=["company_id", "person_id", "start_date"])
    if relevant.empty:
        return adjacency

    fallback_end = pd.Timestamp(current_year, 12, 31)
    for _, group in relevant.groupby("company_id"):
        collapsed = (
            group.groupby("person_id")
            .agg(start_date=("start_date", "min"), end_date=("end_date", "max"))
            .dropna(subset=["start_date"])
            .reset_index()
        )
        if collapsed.empty:
            continue
        intervals = [
            (
                row.person_id,
                row.start_date,
                row.end_date if pd.notna(row.end_date) else fallback_end,
            )
            for row in collapsed.itertuples(index=False)
        ]
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
]

