from __future__ import annotations

import math
from typing import Iterable, Sequence

import pandas as pd


def calculate_relevance_grade(moic: float | None) -> int:
    """Return an integer relevance grade derived from log1p(moic).

    The grade is defined as floor(log1p(moic)) for positive multiples and 0
    for missing or non-positive inputs. Aggregation (e.g. max over a founder's
    historical multiples) is handled by callers before applying this transform.
    This keeps labels compatible with XGBoost's NDCG objective, which requires
    0 or positive integer relevance degrees, while still reflecting the log
    scaling requested in the critique.
    """

    if moic is None:
        return 0
    try:
        value = float(moic)
    except (TypeError, ValueError):
        return 0
    if value <= 0.0:
        return 0
    return int(math.floor(math.log1p(value)))


def parse_eval_metric_k(eval_metric: str | int | None, default: int = 10) -> int:
    """Extract the cutoff k from an eval_metric string like 'ndcg@10'."""

    if eval_metric is None:
        return default
    if isinstance(eval_metric, int):
        return eval_metric
    if isinstance(eval_metric, str):
        if "@" in eval_metric:
            _, k_str = eval_metric.split("@", 1)
            try:
                return int(k_str)
            except ValueError as exc:  # pragma: no cover - config authoring error
                raise ValueError(f"Invalid eval_metric format: {eval_metric}") from exc
    return default


def calculate_ndcg(labels: Sequence[float], scores: Sequence[float], eval_metric: str | int | None = None) -> float:
    """Compute NDCG@k for a single list of labels/scores.

    Args:
        labels: True relevance grades.
        scores: Predicted scores (same length as labels).
        eval_metric: String or int indicating cutoff (e.g., 'ndcg@10').
    """

    if len(labels) != len(scores):
        raise ValueError("labels and scores must have the same length")

    k = parse_eval_metric_k(eval_metric, default=10)
    paired = sorted(zip(labels, scores), key=lambda item: item[1], reverse=True)[:k]

    dcg = _dcg([rel for rel, _ in paired])
    ideal = _dcg(sorted(labels, reverse=True)[:k])
    if ideal == 0:
        return 0.0
    return float(dcg / ideal)


def _dcg(relevances: Iterable[float]) -> float:
    return float(
        sum((math.pow(2.0, rel) - 1.0) / math.log2(idx + 2) for idx, rel in enumerate(relevances))
    )


def compute_cohort_ndcg(
    frame: pd.DataFrame,
    *,
    label_column: str,
    score_column: str,
    cohort_columns: Sequence[str] = ("industry", "company_founded"),
    eval_metric: str | int | None = None,
    min_cohort_size: int = 2,
) -> tuple[pd.DataFrame, float]:
    """Compute NDCG per cohort and return the table plus macro average."""

    if frame.empty:
        columns = list(cohort_columns) + ["count", "ndcg"]
        return pd.DataFrame(columns=columns), 0.0

    rows: list[dict[str, float]] = []
    for cohort_values, cohort_df in frame.groupby(list(cohort_columns)):
        if len(cohort_df) < min_cohort_size:
            continue
        values = cohort_values if isinstance(cohort_values, tuple) else (cohort_values,)
        cohort_entry = {col: val for col, val in zip(cohort_columns, values)}
        ndcg_value = calculate_ndcg(
            cohort_df[label_column].tolist(),
            cohort_df[score_column].tolist(),
            eval_metric,
        )
        cohort_entry["count"] = len(cohort_df)
        cohort_entry["ndcg"] = ndcg_value
        rows.append(cohort_entry)

    if not rows:
        columns = list(cohort_columns) + ["count", "ndcg"]
        return pd.DataFrame(columns=columns), 0.0

    table = pd.DataFrame(rows).sort_values(list(cohort_columns)).reset_index(drop=True)
    macro_ndcg = float(table["ndcg"].mean()) if not table.empty else 0.0
    return table, macro_ndcg


def calculate_mean_ndcg(
    labels: Sequence[float],
    scores: Sequence[float],
    groups: Sequence[int],
    eval_metric: str | int | None = None,
) -> float:
    """Compute the mean NDCG across multiple groups (queries).

    Args:
        labels: Flat list of relevance grades for all groups.
        scores: Flat list of predicted scores for all groups.
        groups: List of group sizes (e.g., [2, 3] means first 2 items are group 1, next 3 are group 2).
        eval_metric: String or int indicating cutoff (e.g., 'ndcg@10').
    """
    if sum(groups) != len(labels):
        raise ValueError("Sum of groups must equal length of labels")
    if len(labels) != len(scores):
        raise ValueError("labels and scores must have the same length")

    ndcg_values = []
    start_idx = 0
    for group_size in groups:
        end_idx = start_idx + group_size
        group_labels = labels[start_idx:end_idx]
        group_scores = scores[start_idx:end_idx]
        
        ndcg = calculate_ndcg(group_labels, group_scores, eval_metric)
        ndcg_values.append(ndcg)
        
        start_idx = end_idx

    if not ndcg_values:
        return 0.0
        
    return float(sum(ndcg_values) / len(ndcg_values))
