from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from heuristic import compute_heuristic_score


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _datasets_root() -> Path:
    return _project_root() / "solution_sets" / "@ datasets" / "processed_data"


def _read_split(name: str) -> pd.DataFrame:
    path = _datasets_root() / f"{name}_post_split_features.csv"
    return pd.read_csv(path)


def _compute_scores(frame: pd.DataFrame, use_company: bool) -> pd.DataFrame:
    scored = compute_heuristic_score(frame, use_company=use_company)
    out = frame.merge(scored[["person_id", "heuristic_score"]], on="person_id", how="left")
    return out


def _print_summary(df: pd.DataFrame, name: str) -> None:
    print(f"[{name}] rows={len(df)} cols={len(df.columns)} score_mean={df['heuristic_score'].mean():.4f}")


def main() -> None:
    train = _read_split("train")
    val = _read_split("val")
    test = _read_split("test")

    scored_train = _compute_scores(train, use_company=False)
    scored_val = _compute_scores(val, use_company=False)
    scored_test = _compute_scores(test, use_company=False)

    _print_summary(scored_train, "train")
    _print_summary(scored_val, "val")
    _print_summary(scored_test, "test")

    def _parse_k(metric: str | int | None, default: int = 20) -> int:
        if metric is None:
            return default
        if isinstance(metric, int):
            return metric
        if isinstance(metric, str) and "@" in metric:
            return int(metric.split("@", 1)[1])
        return default

    def _dcg(rels):
        return float(sum((float(2.0) ** float(r) - 1.0) / math.log2(i + 2) for i, r in enumerate(rels)))

    def _ndcg(labels, scores, metric: str | int | None = None):
        k = _parse_k(metric, default=20)
        paired = sorted(zip(labels, scores), key=lambda t: t[1], reverse=True)[:k]
        dcg = _dcg([rel for rel, _ in paired])
        ideal = _dcg(sorted(labels, reverse=True)[:k])
        if ideal == 0.0:
            return 0.0
        return float(dcg / ideal)

    def _cohort_ndcg(frame: pd.DataFrame, label_column: str, score_column: str, cohort_columns=("industry", "company_founded"), metric: str | int | None = "ndcg@20"):
        rows = []
        for values, grp in frame.groupby(list(cohort_columns)):
            if len(grp) < 2:
                continue
            labels = grp[label_column].tolist()
            scores = grp[score_column].tolist()
            val = _ndcg(labels, scores, metric)
            entry = dict(zip(cohort_columns, values if isinstance(values, tuple) else (values,)))
            entry["count"] = len(grp)
            entry["ndcg"] = val
            rows.append(entry)
        table = pd.DataFrame(rows).sort_values(list(cohort_columns)).reset_index(drop=True)
        macro = float(table["ndcg"].mean()) if not table.empty else 0.0
        return table, macro

    for name, df in ("train", scored_train), ("val", scored_val), ("test", scored_test):
        _, macro = _cohort_ndcg(df, label_column="label", score_column="heuristic_score")
        print(f"[{name}] mean_ndcg@20={macro:.4f}")


if __name__ == "__main__":
    main()