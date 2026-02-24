from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import pandas as pd


@dataclass(slots=True)
class FeatureMetadata:
    feature_columns: list[str]
    entity_column: str = "person_id"


@dataclass(slots=True)
class FeatureMatrix:
    frame: pd.DataFrame
    metadata: FeatureMetadata

    def select_columns(self, columns: Sequence[str] | None = None) -> pd.DataFrame:
        cols = list(columns or self.metadata.feature_columns)
        missing = [col for col in cols if col not in self.frame.columns]
        if missing:
            raise KeyError(f"Missing expected feature columns: {missing}")
        return self.frame[cols]

    @property
    def entities(self) -> Iterable:
        return self.frame[self.metadata.entity_column]

