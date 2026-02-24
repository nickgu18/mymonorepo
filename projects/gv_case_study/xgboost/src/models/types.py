from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
import xgboost as xgb

from src.features.types import FeatureMatrix


@dataclass(slots=True)
class ModelBundle:
    """Model estimator paired with metadata needed for inference."""

    estimator: xgb.XGBRanker
    feature_columns: List[str]
    outcome_lookup: Dict[str, float]

    def predict(self, features: FeatureMatrix) -> pd.Series:
        X = features.select_columns(self.feature_columns)
        scores = self.estimator.predict(X)
        return pd.Series(scores, index=features.frame.index, name="score")
