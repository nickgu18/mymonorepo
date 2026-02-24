"""Data splitting utilities for cohort-aware train/test splits."""

from typing import List, Tuple

import pandas as pd


def split_by_industry(
    df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str,
    train_ratio: float = 0.8,
) -> Tuple[
    pd.DataFrame,
    pd.Series,
    pd.DataFrame,
    pd.Series,
    pd.DataFrame,
    pd.DataFrame,
    List[int],
    List[int],
    List[str],
]:
    """Split data by industry cohorts with temporal ordering."""

    _validate_split_inputs(df, feature_cols, target_col, train_ratio)
    work_df = _prepare_split_frame(df)
    train_df, test_df, train_groups, test_groups, industry_names = _split_industries(
        work_df, train_ratio
    )

    X_train = train_df[feature_cols]
    y_train = train_df[target_col]
    X_test = test_df[feature_cols]
    y_test = test_df[target_col]

    _print_split_summary(work_df, train_df, test_df, train_groups, test_groups)

    return (
        X_train,
        y_train,
        X_test,
        y_test,
        train_df,
        test_df,
        train_groups,
        test_groups,
        industry_names,
    )


def _validate_split_inputs(
    df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str,
    train_ratio: float,
) -> None:
    if not 0 < train_ratio < 1:
        raise ValueError(f"train_ratio must be between 0 and 1, got {train_ratio}")

    required_cols = ["industry", "company_founded", "company_id", "person_id"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"DataFrame missing required columns: {missing}")

    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in DataFrame")

    for col in feature_cols:
        if col not in df.columns:
            raise ValueError(f"Feature column '{col}' not found in DataFrame")


def _prepare_split_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize metadata and drop rows without a valid founding year."""

    work_df = df.copy()

    work_df["industry"] = work_df["industry"].fillna("Other")
    work_df["company_founded"] = pd.to_numeric(work_df["company_founded"], errors="coerce")

    missing_count = work_df["company_founded"].isna().sum()
    if missing_count > 0:
        missing_rows = work_df[work_df["company_founded"].isna()]
        missing_rows.to_csv("missing_company_founded_rows.csv", index=False)
        print(
            f"Dropping {missing_count} rows with missing company_founded "
            f"({missing_count/len(work_df)*100:.2f}%)"
        )
        work_df = work_df.dropna(subset=["company_founded"])

    if len(work_df) == 0:
        raise ValueError("No data remaining after filtering missing company_founded values")

    work_df["company_founded"] = work_df["company_founded"].astype(int)

    work_df = work_df.sort_values(
        by=["industry", "company_founded", "company_id", "person_id"]
    ).reset_index(drop=True)
    work_df.to_csv("work_df.csv", index=False)
    return work_df


def _split_industries(
    work_df: pd.DataFrame,
    train_ratio: float,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[int], List[int], List[str]]:
    train_dfs: List[pd.DataFrame] = []
    test_dfs: List[pd.DataFrame] = []
    train_groups: List[int] = []
    test_groups: List[int] = []
    industry_names: List[str] = []
    dropped_cohorts: List[tuple[str, int]] = []

    for industry, cohort in work_df.groupby("industry", sort=False):
        cohort_size = len(cohort)

        if cohort_size < 2:
            dropped_cohorts.append((industry, cohort_size))
            continue

        train_size = max(1, int(cohort_size * train_ratio))
        train_size = min(train_size, cohort_size - 1)

        train_cohort = cohort.iloc[:train_size]
        test_cohort = cohort.iloc[train_size:]

        train_dfs.append(train_cohort)
        test_dfs.append(test_cohort)
        train_groups.append(len(train_cohort))
        test_groups.append(len(test_cohort))
        industry_names.append(industry)

    if not train_dfs:
        raise ValueError("No valid cohorts remaining after filtering")

    train_df = pd.concat(train_dfs, ignore_index=True)
    test_df = pd.concat(test_dfs, ignore_index=True)

    assert sum(train_groups) == len(train_df), (
        f"train_groups sum ({sum(train_groups)}) != train_df length ({len(train_df)})"
    )
    assert sum(test_groups) == len(test_df), (
        f"test_groups sum ({sum(test_groups)}) != test_df length ({len(test_df)})"
    )

    if dropped_cohorts:
        print(f"\nDropped {len(dropped_cohorts)} small cohorts (< 2 rows):")
        for industry, size in dropped_cohorts:
            print(f"  - {industry}: {size} row(s)")

    return train_df, test_df, train_groups, test_groups, industry_names


def _print_split_summary(
    work_df: pd.DataFrame,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    train_groups: List[int],
    test_groups: List[int],
) -> None:
    print(f"\n=== Split Summary ===")
    print(f"Total samples: {len(work_df)}")
    print(f"Train samples: {len(train_df)} ({len(train_df)/len(work_df)*100:.1f}%)")
    print(f"Test samples: {len(test_df)} ({len(test_df)/len(work_df)*100:.1f}%)")
    print(f"Number of industry cohorts: {len(train_groups)}")
    print(f"\nTrain groups (per industry): {train_groups}")
    print(f"Test groups (per industry): {test_groups}")

    print(f"\n=== Per-Industry Breakdown ===")
    for idx, industry in enumerate(train_df.groupby("industry", sort=False).groups.keys()):
        train_count = train_groups[idx]
        test_count = test_groups[idx]
        total = train_count + test_count

        train_labels = train_df[train_df["industry"] == industry][train_df.columns[-1]]
        test_labels = test_df[test_df["industry"] == industry][test_df.columns[-1]]

        train_label_dist = train_labels.value_counts().to_dict()
        test_label_dist = test_labels.value_counts().to_dict()

        print(f"\n{industry}:")
        print(
            f"  Total: {total} | Train: {train_count} ({train_count/total*100:.1f}%)"
            f" | Test: {test_count} ({test_count/total*100:.1f}%)"
        )
        print(f"  Train labels: {dict(sorted(train_label_dist.items()))}")
        print(f"  Test labels: {dict(sorted(test_label_dist.items()))}")


# save_split_summary removed; simple pipeline avoids CSV logging from splitter
