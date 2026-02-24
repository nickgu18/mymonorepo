from __future__ import annotations

from pathlib import Path
from typing import Mapping, Tuple

import pandas as pd

from src.common import FeatureConfig
from src.data.types import RankingCleanData
from src.features.types import FeatureMatrix, FeatureMetadata

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

_CACHE_FILENAME = "founder_features.parquet"


class FeaturePipeline:
    """Unified feature builder for training and inference."""

    def __init__(
        self,
        cfg: FeatureConfig,
        outcome_lookup: Mapping[str, float] | None = None,
    ) -> None:
        self.cfg = cfg
        self.outcome_lookup = dict(outcome_lookup or {})
        self._cache_path = Path(cfg.registry) / _CACHE_FILENAME


    def build_matrix(self, clean_data: RankingCleanData) -> FeatureMatrix:
        founder_frame = self._build_founder_features(clean_data)
        self._persist_founder_features(founder_frame)

        frame = founder_frame.copy()
        entity_column = "person_id"

        metadata = FeatureMetadata(
            feature_columns=list(self.cfg.selected_columns),
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
        _, founder_ids, founder_history = self._prepare_experience_and_founders(clean_data)
        if len(founder_ids) == 0 or founder_history is None or founder_history.empty:
            return self._empty_founder_frame()
        company_info = clean_data.company_info.copy()
        perf_lookup = (
            company_info.set_index("company_id")["performance"].to_dict() if not company_info.empty else {}
        )
        industry_lookup = (
            company_info.set_index("company_id")["industry"].to_dict() if not company_info.empty else {}
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

        rows: list[dict[str, object]] = []
        for person_id, history in founder_history.groupby("person_id"):
            founder_rows = history[history["is_founder"] == True]
            if founder_rows.empty:
                founder_rows = history
            company_id = self._select_last_company(founder_rows)
            company_history = history[history["company_id"] == company_id]
            if company_history.empty:
                continue

            education_tier, education_level = self._education_features_for(
                str(person_id), edu_tier_lookup, edu_level_lookup
            )

            performance, industry = self._company_context_for(
                str(company_id), perf_lookup, industry_lookup
            )

            row = self._assemble_founder_row(
                str(person_id),
                str(company_id),
                str(industry),
                company_history,
                performance,
                float(education_tier),
                float(education_level),
            )
            rows.append(row)

        if not rows:
            return self._empty_founder_frame()
        return pd.DataFrame(rows)

    def _prepare_experience_and_founders(self, clean_data: RankingCleanData) -> Tuple[pd.DataFrame, list, pd.DataFrame | None]:
        exp = clean_data.experience.copy()
        if exp.empty:
            return exp, [], None
        for col in ("is_founder", "is_executive", "is_c_suite"):
            if col in exp.columns:
                exp[col] = _to_bool_series(exp[col])
            else:
                exp[col] = False
        exp["start_date"] = pd.to_datetime(exp.get("start_date"), errors="coerce")
        exp["end_date"] = pd.to_datetime(exp.get("end_date"), errors="coerce")
        exp["exit_moic"] = exp["company_id"].map(self.outcome_lookup)
        ids = exp.loc[exp["is_founder"] == True, "person_id"].dropna().unique().tolist()
        if len(ids) == 0:
            return exp, [], None
        hist = exp[exp["person_id"].isin(ids)].copy()
        return exp, ids, hist

    def _select_last_company(self, founder_rows: pd.DataFrame) -> str:
        rows = founder_rows.copy()
        if "company_id" in rows.columns:
            rows = rows[rows["company_id"].notna()]
            if rows.empty:
                rows = founder_rows
        if "order" in rows.columns:
            try:
                target_row = rows.sort_values(by=["order"], ascending=False).iloc[0]
            except Exception:
                target_row = rows.iloc[-1]
        else:
            if rows.get("start_date") is not None and rows["start_date"].notna().any():
                target_row = rows.sort_values(by=["start_date"], ascending=False).iloc[0]
            else:
                target_row = rows.iloc[-1]
        return str(target_row["company_id"])

    def _education_features_for(self, person_id: str, edu_tier_lookup: dict, edu_level_lookup: dict) -> Tuple[float, float]:
        education_tier = float(edu_tier_lookup.get(person_id, 1.0))
        if pd.isna(education_tier):
            education_tier = 1.0
        education_level = float(edu_level_lookup.get(person_id, _score_degree(None)))
        return education_tier, education_level

    def _company_context_for(self, company_id: str, perf_lookup: dict, industry_lookup: dict) -> Tuple[float, str]:
        raw_perf = perf_lookup.get(company_id)
        performance = (
            float(raw_perf) if raw_perf is not None and not pd.isna(raw_perf) else float("nan")
        )
        industry = industry_lookup.get(company_id, "unknown")
        return performance, industry

    def _assemble_founder_row(
        self,
        person_id: str,
        company_id: str,
        industry: str,
        company_history: pd.DataFrame,
        performance: float,
        education_tier: float,
        education_level: float,
    ) -> dict:
        row = {
            "person_id": person_id,
            "company_id": company_id,
            "industry": industry,
            "is_founder_of_target": bool(company_history["is_founder"].any()),
            "performance": performance,
            "education_tier": education_tier,
            "education_level_score": education_level,
        }
        return row

    def _persist_founder_features(self, frame: pd.DataFrame) -> None:
        try:
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            frame.to_parquet(self._cache_path, index=False)
        except Exception:  # pragma: no cover - persistence best-effort
            return

    def _empty_founder_frame(self) -> pd.DataFrame:
        return pd.DataFrame(
            columns=[
                "person_id",
                "company_id",
                "industry",
                "is_founder_of_target",
                "performance",
                "education_tier",
                "education_level_score",
            ]
        )


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
