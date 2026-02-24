from __future__ import annotations

import pandas as pd

from src.common import FeatureConfig
from src.data.types import RankingCleanData
from src.features.pipeline import FeaturePipeline, _to_bool_series
from src.features.types import FeatureMatrix
from src.models.metrics import calculate_relevance_grade


def build_training_dataset(
    clean_training: RankingCleanData,
    clean_ranking: RankingCleanData,
    target_df: pd.DataFrame,
    feature_cfg: FeatureConfig,
) -> pd.DataFrame:
    """Build the labeled founder training frame for the ranker.

    1) Build founder-level features via FeaturePipeline (one row per founder).
    2) Join target metadata (company_founded, multiple, industry).
    3) Derive integer labels from multiples.
    4) Remove founders whose last founded company appears in the ranking data.
    5) Coerce company_founded to numeric for downstream splitting.
    """

    # Step 3.1: founder-level features (one row per founder, last founded company).
    train_fm: FeatureMatrix = FeaturePipeline(feature_cfg).build_matrix(clean_training)
    train_df = train_fm.frame.copy()

    # Step 3.2: attach targets and metadata.
    targets = target_df[["company_id", "company_founded", "multiple", "industry"]].copy()
    targets.rename(columns={"industry": "target_industry"}, inplace=True)
    joined = train_df.merge(targets, on="company_id", how="left")

    joined["industry"] = joined["industry"].fillna("Other").replace({"unknown": "Other"})
    mask_other = (joined["industry"] == "Other") & joined["target_industry"].notna()
    joined.loc[mask_other, "industry"] = joined.loc[mask_other, "target_industry"].astype(str)
    joined.drop(columns=["target_industry"], inplace=True)

    # Derive integer labels from multiple using the shared relevance grade helper.
    joined[feature_cfg.target_column] = (
        joined["multiple"].fillna(0.0).astype(float).apply(calculate_relevance_grade)
    )
    # Keep only metadata + label from the target table; multiple is no longer needed downstream.
    joined.drop(columns=["multiple"], inplace=True)

    # Leakage removal: drop founders whose last founded company also appears in the
    # ranking (inference) dataset, based on company_id.
    rank_exp = clean_ranking.experience.copy()
    if "is_founder" in rank_exp.columns:
        rank_exp["is_founder"] = _to_bool_series(rank_exp["is_founder"])
        rank_founders = rank_exp[rank_exp["is_founder"] == True].copy()  # noqa: E712
        if not rank_founders.empty:
            rank_founders = rank_founders.sort_values(["person_id", "order"])
            last_rank = rank_founders.groupby("person_id", as_index=False).tail(1)
            last_company_ids = set(last_rank["company_id"].astype(str))
            keep_mask = ~joined["company_id"].astype(str).isin(last_company_ids)
            joined = joined.loc[keep_mask].reset_index(drop=True)

    # Ensure company_founded is numeric for downstream splitting; rows with missing
    # founding year are filtered later by splitters, not here.
    joined["company_founded"] = pd.to_numeric(joined.get("company_founded"), errors="coerce")

    return joined
