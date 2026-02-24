from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Mapping

import pandas as pd

from src.common import FeatureConfig
from src.data.types import RankingCleanData
from src.features.types import FeatureMatrix, FeatureMetadata

_EXIT_BINS = (
    ("tiered_exit_1x", 1.0, 3.0),
    ("tiered_exit_3x", 3.0, 10.0),
    ("tiered_exit_10x", 10.0, 50.0),
    ("tiered_exit_50x", 50.0, 100.0),
    ("tiered_exit_100x", 100.0, float("inf")),
)

_DEGREE_SCORE_MAP = {
    "phd": 5.0,
    "doctorate": 5.0,
    "masters": 4.0,
    "master": 4.0,
    "mba": 4.0,
    "bachelors": 3.0,
    "bachelor": 3.0,
    "ba": 3.0,
    "bs": 3.0,
    "undergraduate": 3.0,
    "associates": 2.0,
    "associate": 2.0,
    "aa": 2.0,
    "highschool": 1.0,
    "high_school": 1.0,
    "high school": 1.0,
    "hs": 1.0,
    "ged": 1.0,
}

_VELOCITY_WINDOW_YEARS = 5
_CACHE_FILENAME = "founder_features.parquet"


class FeaturePipeline:
    """Unified feature builder for training and inference."""

    def __init__(
        self,
        cfg: FeatureConfig,
        outcome_lookup: Mapping[str, float] | None = None,
        company_founded_lookup: Mapping[str, float] | None = None,
    ) -> None:
        self.cfg = cfg
        self.outcome_lookup = dict(outcome_lookup or {})
        self.company_founded_lookup = {k: v for k, v in (company_founded_lookup or {}).items()}
        self._cache_path = Path(cfg.registry) / _CACHE_FILENAME

    '''
    Imputation function for missing values, user specifiy methods of imputation
    '''
    def impute_field(self, clean_data: RankingCleanData, column: str, method: str = "median") -> RankingCleanData:
        column_name = f'{column}_{method}'
        if method == "median":
            clean_data[column_name] = clean_data[column].fillna(clean_data[column].median())
        elif method == "mean":
            clean_data[column_name] = clean_data[column].fillna(clean_data[column].mean())
        elif method == "zero":
            clean_data[column_name] = clean_data[column].fillna(0)
        else:
            raise ValueError(f"Invalid imputation method: {method}")
        return clean_data[column_name]

    def build_matrix(self, clean_data: RankingCleanData) -> FeatureMatrix:
        founder_frame = self._build_founder_features(clean_data)
        self._persist_founder_features(founder_frame)

        frame = founder_frame.copy()
        entity_column = "person_id"

        metadata = FeatureMetadata(
            feature_columns=list(self.cfg.numerical_columns + self.cfg.categorical_columns),
            entity_column=entity_column,
        )
        missing = [col for col in metadata.feature_columns if col not in frame.columns]
        if missing:
            raise KeyError(f"Missing expected feature columns: {missing}")

        id_columns = [col for col in ("person_id", "company_id") if col in frame.columns]
        ordered_cols = id_columns + metadata.feature_columns + [
            c for c in frame.columns if c not in id_columns + metadata.feature_columns
        ]
        return FeatureMatrix(frame=frame[ordered_cols].reset_index(drop=True), metadata=metadata)

    # ---------------------------------------------------------------------
    # Feature engineering helpers

    def _build_founder_features(self, clean_data: RankingCleanData) -> pd.DataFrame:
        experience = clean_data.experience.copy()
        if experience.empty:
            return self._empty_founder_frame()

        for col in ("is_founder", "is_executive", "is_c_suite"):
            if col in experience.columns:
                experience[col] = _to_bool_series(experience[col])
            else:  # pragma: no cover - legacy schemas
                experience[col] = False

        experience["start_date"] = pd.to_datetime(experience.get("start_date"), errors="coerce")
        experience["end_date"] = pd.to_datetime(experience.get("end_date"), errors="coerce")
        experience["exit_moic"] = experience["company_id"].map(self.outcome_lookup)

        founder_ids = experience.loc[experience["is_founder"] == True, "person_id"].dropna().unique()
        if len(founder_ids) == 0:
            return self._empty_founder_frame()

        founder_history = experience[experience["person_id"].isin(founder_ids)].copy()
        company_info = clean_data.company_info.copy()
        company_info["company_founded"] = pd.to_numeric(
            company_info.get("company_founded"), errors="coerce"
        )
        company_context = company_info.set_index("company_id") if not company_info.empty else None
        perf_lookup = (
            company_info.set_index("company_id")["performance"].to_dict() if not company_info.empty else {}
        )
        industry_lookup = (
            company_info.set_index("company_id")["industry"].to_dict() if not company_info.empty else {}
        )
        founded_lookup = {**self.company_founded_lookup}
        if company_context is not None and "company_founded" in company_context.columns:
            founded_lookup.update(
                company_context["company_founded"].dropna().astype(float).to_dict()
            )

        education = clean_data.education.copy()
        edu_tier_lookup = (
            education.set_index("person_id")["education_tier"].astype(float).to_dict()
            if not education.empty
            else {}
        )
        edu_level_lookup: dict[str, float] = {}
        if not education.empty and "highest_level" in education.columns:
            edu_level_lookup = {
                pid: _score_degree(level)
                for pid, level in education.set_index("person_id")["highest_level"].items()
            }

        team_size_map = (
            founder_history.loc[founder_history["is_founder"] == True]
            .groupby("company_id")["person_id"]
            .nunique()
            .to_dict()
        )

        adjacency = _build_co_worker_adjacency(experience, current_year=self.cfg.current_year)
        for founder_id in founder_ids:
            adjacency.setdefault(founder_id, set())
        component_sizes = _component_sizes(adjacency)
        network_quality_map = _network_quality(adjacency, edu_tier_lookup)

        rows: list[dict[str, object]] = []
        for person_id, history in founder_history.groupby("person_id"):
            founder_companies = (
                history.loc[history["is_founder"] == True, "company_id"].dropna().unique()
            )
            if len(founder_companies) == 0:
                founder_companies = history["company_id"].dropna().unique()

            for company_id in founder_companies:
                company_history = history[history["company_id"] == company_id]
                if company_history.empty:
                    continue

                t0_year = founded_lookup.get(company_id)
                if t0_year is None or pd.isna(t0_year):
                    t0_year = float(self.cfg.current_year)
                try:
                    year_int = int(t0_year)
                except (TypeError, ValueError):  # pragma: no cover - defensive
                    year_int = int(self.cfg.current_year)
                t0_date = pd.Timestamp(year_int, 1, 1)
                window_start = t0_date - pd.DateOffset(years=_VELOCITY_WINDOW_YEARS)

                prior = history[
                    (history["company_id"] != company_id)
                    & history["start_date"].notna()
                    & (history["start_date"] < t0_date)
                ].copy()
                prior = prior[prior["end_date"].isna() | (prior["end_date"] <= t0_date)]
                prior["end_date"] = prior["end_date"].fillna(t0_date)

                role_durations = [
                    max((row.end_date - row.start_date).days, 0) / 365.25
                    for row in prior.itertuples()
                ]
                avg_role_duration = float(sum(role_durations) / len(role_durations)) if role_durations else 0.0

                prior_window = prior[prior["start_date"] >= window_start]
                role_velocity = int(len(prior_window))
                job_type_mask = False
                if "job_type" in prior_window.columns:
                    job_type_mask = prior_window["job_type"].str.contains(
                        "founder", case=False, na=False
                    )
                exec_window = prior_window[
                    (prior_window["is_executive"] == True)
                    | (prior_window["is_c_suite"] == True)
                    | (prior_window["is_founder"] == True)
                    | job_type_mask
                ]
                exec_role = int(len(exec_window) > 0)

                exit_counts = {name: 0 for name, *_ in _EXIT_BINS}
                for moic in prior["exit_moic"].dropna().astype(float).tolist():
                    for name, lower, upper in _EXIT_BINS:
                        if lower <= moic < upper:
                            exit_counts[name] += 1
                            break

                earliest_start = prior["start_date"].min()
                if pd.isna(earliest_start):
                    experience_span = 0.0
                else:
                    experience_span = max((t0_date - earliest_start).days / 365.25, 0.0)

                education_tier = float(edu_tier_lookup.get(person_id, 1.0))
                if pd.isna(education_tier):
                    education_tier = 1.0
                education_level = float(edu_level_lookup.get(person_id, _score_degree(None)))

                raw_perf = perf_lookup.get(company_id)
                performance = (
                    float(raw_perf)
                    if raw_perf is not None and not pd.isna(raw_perf)
                    else float("nan")
                )
                industry = industry_lookup.get(company_id, "unknown")
                team_size = float(team_size_map.get(company_id, 1))
                direct_network = float(len(adjacency.get(person_id, set())))
                indirect_network = float(component_sizes.get(person_id, 0))
                network_quality = float(network_quality_map.get(person_id, 0.0))

                rows.append(
                    {
                        "person_id": person_id,
                        "company_id": company_id,
                        "industry": industry,
                        "founded_year": year_int,
                        "is_founder_of_target": bool(company_history["is_founder"].any()),
                        "performance": performance,
                        "experience_span_years": float(experience_span),
                        "average_role_duration_years": avg_role_duration,
                        "role_velocity_5yr": role_velocity,
                        "exec_role_5yr": exec_role,
                        "education_tier": education_tier,
                        "education_level_score": education_level,
                        "direct_network_size": direct_network,
                        "indirect_network_size": indirect_network,
                        "network_quality": network_quality,
                        "team_size": team_size,
                        **exit_counts,
                    }
                )

        if not rows:
            return self._empty_founder_frame()
        return pd.DataFrame(rows)

    def _persist_founder_features(self, frame: pd.DataFrame) -> None:
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            frame.to_parquet(self._cache_path, index=False)
        except Exception:  # pragma: no cover - persistence best-effort
            return

    def _empty_founder_frame(self) -> pd.DataFrame:
        base_columns = [
            "person_id",
            "company_id",
            "industry",
            "founded_year",
            "is_founder_of_target",
        ]
        for col in self.cfg.numerical_columns:
            if col not in base_columns:
                base_columns.append(col)
        return pd.DataFrame(columns=base_columns)


def _to_bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    normalized = series.fillna("").astype(str).str.strip().str.lower()
    truthy = {"true", "1", "yes", "y", "t"}
    return normalized.apply(lambda value: value in truthy)


def _score_degree(value) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 1.0
    text = str(value).strip().lower()
    if not text:
        return 1.0
    return _DEGREE_SCORE_MAP.get(text, 1.0)


def _build_co_worker_adjacency(experience: pd.DataFrame, current_year: int) -> dict[str, set[str]]:
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


def _intervals_overlap(start_a: pd.Timestamp, end_a: pd.Timestamp, start_b: pd.Timestamp, end_b: pd.Timestamp) -> bool:
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
