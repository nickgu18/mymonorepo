from __future__ import annotations

import pandas as pd

from src.features import FeatureMatrix
from src.models import ModelBundle
from src.predict.explanations import summarize_shap


def predict_batch(bundle: ModelBundle, features: FeatureMatrix, shap_top_n: int = 3) -> pd.DataFrame:
    """Pure prediction entrypoint: no config or IO side effects."""

    X_rank = features.select_columns(bundle.feature_columns)
    scores = bundle.predict(features)
    df = features.frame.copy()
    df["score"] = scores
    df["rank"] = df["score"].rank(ascending=False, method="dense").astype(int)

    if shap_top_n > 0:
        explanations = summarize_shap(bundle.estimator, X_rank, top_k=shap_top_n)
    else:
        explanations = pd.Series(["" for _ in range(len(df))], index=df.index, name="explanation")
    df["explanation"] = explanations

    renamed = df.rename(columns={"person_id": "founder_id"})
    column_order = ["founder_id", "industry", "company_founded", "score", "rank", "explanation"]
    available_columns = [col for col in column_order if col in renamed.columns]
    return (
        renamed[available_columns]
        .sort_values("rank")
        .reset_index(drop=True)
    )
