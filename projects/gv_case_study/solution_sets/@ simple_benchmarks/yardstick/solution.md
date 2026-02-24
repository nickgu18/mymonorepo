# Simple Yardstick: Heuristic Founder Score (PIT-aware)

This doc defines a single baseline: a hand-crafted founder score computed on point-in-time features, implemented with modular subscores.

## PIT Inputs
- One row per founder built PIT-clean as of `as_of_date`.
- Base features: `education_tier`, `education_level_score`, `performance` (optional).
- Aggregates used in splits: `founder_has_perf`, `founder_perf_mean`, `founder_perf_max`, `founder_perf_last`, `network_size_1st`, `network_quality_1st`, `team_size`.

## Scoring
```python
from solution_sets.simple_benchmarks.yardstick.heuristic import (
    build_basic_features,
    build_experience_features,
    build_performance_features,
    build_network_features,
    build_company_features,
    compute_heuristic_score,
)
```

## Evaluation
- On PIT splits, compute `heuristic_score` and NDCG vs `label_grade`.
- Rank within industry or globally; report mean NDCG@k.

## Final Output
```python
import numpy as np

def build_ranked_founders(df, score_col, explanation_template):
    out = df.copy()
    out = out.sort_values(score_col, ascending=False).reset_index(drop=True)
    out["rank"] = np.arange(1, len(out) + 1)
    out["explanation"] = out.apply(
        lambda row: explanation_template.format(
            edu_tier=row.get("education_tier", np.nan),
            num_founded=row.get("team_size", np.nan),
            perf=row.get("performance", np.nan),
        ),
        axis=1,
    )
    return out[["person_id", score_col, "rank", "explanation"]].rename(columns={"person_id": "founder_id", score_col: "score"})
```

Example explanation template:
```python
template = (
    "Higher score due to education tier {edu_tier}, "
    "team size {num_founded}, "
    "and company performance {perf:.2f}."
)
```