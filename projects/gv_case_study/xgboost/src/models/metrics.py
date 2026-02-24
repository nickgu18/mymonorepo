from __future__ import annotations

import math
from typing import Iterable, Sequence


# Converted from log1p(multiple)
DEFAULT_RECALL_THRESHOLD = 3


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


def calculate_recall(
    labels: Sequence[float], scores: Sequence[float], eval_metric: str | int | None = None,
    threshold: float = DEFAULT_RECALL_THRESHOLD,
) -> float:
    if len(labels) != len(scores):
        raise ValueError("labels and scores must have the same length")
    k = parse_eval_metric_k(eval_metric, default=10)
    paired = sorted(zip(labels, scores), key=lambda item: item[1], reverse=True)[:k]
    relevant_in_top_k = sum(1 for rel, _ in paired if rel > threshold)
    total_relevant = sum(1 for rel in labels if rel > threshold)
    if total_relevant == 0:
        return 0.0
    return float(relevant_in_top_k / total_relevant)


def calculate_mean_recall(
    labels: Sequence[float],
    scores: Sequence[float],
    groups: Sequence[int],
    eval_metric: str | int | None = None,
    threshold: float = DEFAULT_RECALL_THRESHOLD,
) -> float:
    if sum(groups) != len(labels):
        raise ValueError("Sum of groups must equal length of labels")
    if len(labels) != len(scores):
        raise ValueError("labels and scores must have the same length")
    recall_values = []
    start_idx = 0
    for group_size in groups:
        end_idx = start_idx + group_size
        group_labels = labels[start_idx:end_idx]
        group_scores = scores[start_idx:end_idx]
        recall_val = calculate_recall(group_labels, group_scores, eval_metric, threshold)
        recall_values.append(recall_val)
        start_idx = end_idx
    if not recall_values:
        return 0.0
    return float(sum(recall_values) / len(recall_values))
