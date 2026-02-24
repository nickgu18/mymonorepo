from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd


def summarize_shap(estimator, feature_frame: pd.DataFrame, top_k: int = 3) -> pd.Series:
    """Return lightweight SHAP summaries for each row."""

    if top_k <= 0 or feature_frame.empty:
        return pd.Series(["" for _ in range(len(feature_frame))], index=feature_frame.index, name="explanation")

    import shap  # Lazy import so training environments avoid the dependency

    explainer = shap.TreeExplainer(estimator)
    shap_values = explainer.shap_values(feature_frame)
    if isinstance(shap_values, list):  # Some explainers return per-class arrays
        shap_array = np.asarray(shap_values[0])
    else:
        shap_array = np.asarray(shap_values)

    messages: list[str] = []
    columns = feature_frame.columns.tolist()
    for idx, row_values in enumerate(shap_array):
        ranked = sorted(zip(columns, row_values), key=lambda item: abs(item[1]), reverse=True)[:top_k]
        if not ranked:
            messages.append("")
            continue
        formatted = ", ".join(f"{name} ({value:+.2f})" for name, value in ranked)
        messages.append(f"Top factors: {formatted}")
    return pd.Series(messages, index=feature_frame.index, name="explanation")
