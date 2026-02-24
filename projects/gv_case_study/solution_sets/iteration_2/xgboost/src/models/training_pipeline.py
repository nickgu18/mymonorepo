from __future__ import annotations

import pandas as pd

from src.common import FeatureConfig
from src.data.types import RankingCleanData
from src.features.pipeline import FeaturePipeline, _to_bool_series
from src.features.types import FeatureMatrix
from src.models.metrics import calculate_relevance_grade


def _build_last_labeled_company_metadata(
    clean_training: RankingCleanData,
    target_df: pd.DataFrame,
) -> pd.DataFrame:
    """Return one row per founder with metadata for their last labeled company.

    A labeled company is any company_id that appears in target_variable_training.
    For each founder, we select the experience row with the largest `order`
    whose company_id is present in the target table, then attach
    (company_founded, multiple, industry, performance).
    """

    experience = clean_training.experience.copy()
    company_info = clean_training.company_info.copy()

    if "is_founder" not in experience.columns:
        raise ValueError("Expected 'is_founder' column in training experience data")

    experience["is_founder"] = _to_bool_series(experience["is_founder"])
    founder_rows = experience[experience["is_founder"] == True].copy()  # noqa: E712
    founder_rows = founder_rows[founder_rows["company_id"].notna()].copy()

    # Prepare normalized targets with performance for label companies.
    targets = target_df[["company_id", "company_founded", "multiple", "industry"]].copy()
    targets = targets.merge(
        company_info[["company_id", "performance"]],
        on="company_id",
        how="left",
    )

    # Restrict to experiences whose company_id has a label.
    founder_rows["company_id"] = founder_rows["company_id"].astype(str)
    targets["company_id"] = targets["company_id"].astype(str)
    labeled_exp = founder_rows.merge(targets, on="company_id", how="inner")

    if labeled_exp.empty:
        raise ValueError("No founder experiences with labels found in target data")

    # Select the last labeled company per founder by `order`.
    labeled_exp = labeled_exp.sort_values(["person_id", "order"])
    last_labeled = labeled_exp.groupby("person_id", as_index=False).tail(1)

    metadata = last_labeled[
        [
            "person_id",
            "company_id",
            "industry",
            "company_founded",
            "multiple",
            "performance",
        ]
    ].copy()
    metadata.rename(
        columns={
            "company_id": "label_company_id",
            "industry": "label_industry",
            "performance": "label_performance",
        },
        inplace=True,
    )
    return metadata


def build_training_dataset(
    clean_training: RankingCleanData,
    clean_ranking: RankingCleanData,
    target_df: pd.DataFrame,
    feature_cfg: FeatureConfig,
) -> pd.DataFrame:
    """Build the labeled founder training frame for the ranker.

    1) Build founder-level features via FeaturePipeline (one row per founder).
    2) Attach label metadata for the last labeled company per founder.
    3) Derive integer labels from multiples.
    4) Remove founders whose labeled company appears in the ranking data.
    5) Coerce company_founded to numeric for downstream splitting.
    """

    # Step 3.1: founder-level features (one row per founder, last founded company).
    train_fm: FeatureMatrix = FeaturePipeline(feature_cfg).build_matrix(clean_training)
    features_df = train_fm.frame.copy()

    # Step 3.2: attach label metadata using the last company with a target for each founder.
    label_meta = _build_last_labeled_company_metadata(clean_training, target_df)

    # Join on person_id to keep one row per founder and align metadata with features.
    joined = features_df.merge(label_meta, on="person_id", how="inner")

    # Override company_id / industry / performance to reflect the labeled company.
    joined["company_id"] = joined["label_company_id"]
    joined["industry"] = joined["label_industry"].fillna("Other").replace({"unknown": "Other"})
    joined["performance"] = joined["label_performance"]
    joined.drop(columns=["label_company_id", "label_industry", "label_performance"], inplace=True)

    # Derive integer labels from multiple using the shared relevance grade helper.
    joined[feature_cfg.target_column] = (
        joined["multiple"].fillna(0.0).astype(float).apply(calculate_relevance_grade)
    )
    # Keep only metadata + label from the target table; multiple is no longer needed downstream.
    joined.drop(columns=["multiple"], inplace=True)

    # Leakage removal: drop founders whose labeled company also appears in the
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

    # Ensure company_founded is numeric and drop rows where the founding year
    # is missing so downstream splitters see only fully specified founders.
    joined["company_founded"] = pd.to_numeric(joined.get("company_founded"), errors="coerce")
    joined = joined.dropna(subset=["company_founded"]).reset_index(drop=True)

    return joined
