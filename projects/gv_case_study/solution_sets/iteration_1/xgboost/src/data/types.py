from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(slots=True)
class RankingRawData:
    """Container for the three CSVs powering founder ranking."""

    experience: pd.DataFrame
    education: pd.DataFrame
    company_info: pd.DataFrame
    schema_version: str
    source_dir: Path


@dataclass(slots=True)
class RankingCleanData:
    """Validated, normalized dataset consumed by feature builders."""

    experience: pd.DataFrame
    education: pd.DataFrame
    company_info: pd.DataFrame

