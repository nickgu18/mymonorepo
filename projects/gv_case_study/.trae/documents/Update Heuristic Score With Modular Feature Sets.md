## Data Review
- Location: `solution_sets/@ datasets/processed_data/*`
- Shared columns across splits: `person_id`, `company_id`, `industry`, `is_founder_of_target`, `performance`, `education_tier`, `education_level_score`, `label_company_id`, `label_max_founder_multiple`, `label_company_founded_year`, `label_company_industry`, `company_founded`, `label`.
- Added aggregates in split files: `founder_has_perf`, `founder_perf_mean`, `founder_perf_max`, `founder_perf_last`, `network_size_1st`, `network_quality_1st`, `team_size`.

## Notebook Columns (Iteration 5)
- Iteration 5 notebook references the added aggregates and includes them in the feature list: `founder_has_perf`, `founder_perf_mean`, `founder_perf_max`, `founder_perf_last`, `network_quality_1st`, `network_size_1st`, `team_size`.
- Config `features.selected_columns` currently contains only: `performance`, `education_tier`, `education_level_score`.
- Notebook uses `cfg.features.selected_columns` plus the aggregated features, and sometimes excludes raw `performance` to avoid leakage.

## Heuristic Design (Simple, Modular)
- Goal: Single-score yardstick built from PIT-safe features with clear sub-scores.
- Subsets and sources:
  - Basic: `education_tier`, `education_level_score`.
  - Experience: `is_founder_of_target` (binary), `team_size` (proxy for leadership scope).
  - Performance: `founder_has_perf`, `founder_perf_mean`, `founder_perf_max`, `founder_perf_last`.
  - Network: `network_quality_1st`, `network_size_1st`.
  - Optional Company: `performance` (label company performance) — can be toggled on/off.
- Normalization:
  - Fill NA to sensible defaults: zeros for counts/scores, `False` for booleans.
  - Per-column scaling to [0,1] using dataset maxima with floor guards (≥1) to avoid divide-by-zero.
- Weighting (initial simple weights):
  - `performance_subscore`: 0.30
  - `network_subscore`: 0.25
  - `basic_subscore`: 0.25
  - `experience_subscore`: 0.20
  - Optional company factor: 0.10 (if enabled, proportionally reduce others or treat it as part of performance).
- Output: `heuristic_score` in [0,1], deterministic, no training.

## Function Split (Proposed API)
- `build_basic_features(df) -> pd.DataFrame` with `basic_subscore`.
- `build_experience_features(df) -> pd.DataFrame` with `experience_subscore`.
- `build_performance_features(df) -> pd.DataFrame` with `performance_subscore`.
- `build_network_features(df) -> pd.DataFrame` with `network_subscore`.
- `build_company_features(df, enabled=True) -> pd.DataFrame` with `company_subscore`.
- `compute_heuristic_score(df, use_company=True) -> pd.DataFrame` that merges subscores and returns `heuristic_score`.
- All functions operate on the split feature tables (`train_post_split_features.csv`, `val_post_split_features.csv`, `test_post_split_features.csv`) and the ranking dataset when needed.

## Implementation Plan
- Add a Python module `solution_sets/simple_benchmarks/yardstick/heuristic.py` implementing the functions above.
- Update doc in `solution_sets/simple_benchmarks/yardstick/solution.md` to describe the modular yardstick and its formula.
- Provide a small driver notebook/script to compute and save `heuristic_score` for train/val/test to compare NDCG vs `label`.
- Ensure missing columns are handled gracefully (e.g., if a subset is absent in ranking data, only use available subsets and re-normalize weights).

## Evaluation
- Compute scores on `train_post_split_features.csv`, `val_post_split_features.csv`, `test_post_split_features.csv`.
- Report mean NDCG@20 per industry and globally against `label`.
- Sensitivity check: run once with `use_company=False` to mirror notebook’s exclusion of raw `performance`.

## File Changes
- New: `solution_sets/simple_benchmarks/yardstick/heuristic.py` (modular functions).
- Update: `solution_sets/simple_benchmarks/yardstick/solution.md` (describe modular heuristic).
- Optional: `solution_sets/simple_benchmarks/yardstick/eval.ipynb` or `scripts/eval_heuristic.py` for quick NDCG evaluation.

## Next Steps
- Confirm the plan and preferred default for `use_company` (on or off).
- After confirmation, implement the module, update the doc, and run evaluation on the processed datasets to validate improvements.
