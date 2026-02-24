from __future__ import annotations

from pathlib import Path
import pandas as pd
from src.common import DataConfig
from src.common.exceptions import DataLoadError
from src.data.types import RankingCleanData, RankingRawData

_REQUIRED_EXPERIENCE_COLS = ("person_id", "company_id", "start_date", "end_date")
_REQUIRED_EDUCATION_COLS = ("person_id", "education_tier")
_REQUIRED_COMPANY_INFO_COLS = ("company_id", "industry", "performance")
_REQUIRED_TARGET_COLS = ("company_id", "industry", "company_founded", "multiple")


def require_columns(frame: pd.DataFrame, required: tuple[str, ...], source: str) -> None:
    """Ensure the frame contains all required columns."""

    missing = [col for col in required if col not in frame.columns]
    if missing:
        raise DataLoadError(path=source, message=f"Missing columns: {missing}")


# load_and_clean removed; notebooks should call load_raw + clean explicitly


def load_raw(cfg: DataConfig, dataset: str = "ranking") -> RankingRawData:
    """Load raw CSVs for the founder ranking task.

    Args:
        cfg: data configuration contract.
        dataset: "ranking" (default) uses cfg.raw_dir + cfg.ranking_files;
                 "training" uses cfg.curated_dir + cfg.training_files.
    """

    if dataset not in {"ranking", "training"}:
        raise DataLoadError(path=str(cfg.raw_dir), message=f"unknown dataset '{dataset}'")

    use_training = dataset == "training"
    source_dir = cfg.curated_dir if use_training else cfg.raw_dir
    file_set = cfg.training_files if use_training else cfg.ranking_files
    if file_set is None:
        raise DataLoadError(path=str(source_dir), message="data file mapping not configured")
    paths = {
        "experience": source_dir / file_set.founder_experience,
        "education": source_dir / file_set.education,
        "company_info": source_dir / file_set.company_info,
    }
    frames = {}
    for name, path in paths.items():
        try:
            frames[name] = pd.read_csv(path)
        except FileNotFoundError as exc:  # pragma: no cover - trivial
            raise DataLoadError(path=str(path)) from exc

    require_columns(frames["experience"], _REQUIRED_EXPERIENCE_COLS, "founder_experience")
    require_columns(frames["education"], _REQUIRED_EDUCATION_COLS, "education")
    require_columns(frames["company_info"], _REQUIRED_COMPANY_INFO_COLS, "company_info")

    return RankingRawData(
        experience=frames["experience"],
        education=frames["education"],
        company_info=frames["company_info"],
        schema_version=cfg.schema_version or "unknown",
        source_dir=source_dir,
    )


def load_targets(cfg: DataConfig) -> pd.DataFrame:
    """Load the curated target dataset including founding metadata."""

    path = cfg.training_file
    try:
        targets = pd.read_csv(path)
    except FileNotFoundError as exc:  # pragma: no cover - trivial
        raise DataLoadError(path=str(path)) from exc

    require_columns(targets, _REQUIRED_TARGET_COLS, "target_variable_training")
    return normalize_ids(targets)


# company_founded_lookup removed; founded year is sourced via targets join in training pipeline


def clean(raw: RankingRawData) -> RankingCleanData:
    """Normalize IDs, dedupe, parse dates, and coerce performance to numeric.

    Missing values in the performance column are preserved as NaN so that
    downstream models (e.g. XGBoost) can leverage their built-in handling.
    """

    def clean_experience(df: pd.DataFrame) -> pd.DataFrame:
        # clean dates
        df = parse_dates(df)
        # normalize ids
        df = normalize_ids(df)
        return df

    def clean_education(df: pd.DataFrame) -> pd.DataFrame:
        # normalize ids
        df = normalize_ids(df)
        return df

    def clean_company_info(df: pd.DataFrame) -> pd.DataFrame:
        # normalize ids
        df = normalize_ids(df)
        # coerce performance to numeric
        # Convert the 'performance' column to a numeric type.
        # The `errors='coerce'` argument ensures that any values that cannot be
        # converted to a number are replaced with `NaN` (Not a Number) instead of
        # raising an error, allowing the operation to complete gracefully.
        df["performance"] = pd.to_numeric(df.get("performance"), errors="coerce")
        return df

    exp = clean_experience(raw.experience)
    edu = clean_education(raw.education)
    ci = clean_company_info(raw.company_info)

    clean = RankingCleanData(
        experience=exp,
        education=edu,
        company_info=ci,
    )
    return clean


def normalize_ids(df: pd.DataFrame) -> pd.DataFrame:

    def clean_id(value):
        if isinstance(value, str):
            return value.replace("/p/", "").replace("/c/", "")
        return value

    df = df.copy()
    for col in df.columns:
        if "id" in col:
            df[col] = df[col].apply(clean_id)
    return df


def parse_dates(df: pd.DataFrame, cols=("start_date", "end_date")) -> pd.DataFrame:
    df = df.copy()
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df