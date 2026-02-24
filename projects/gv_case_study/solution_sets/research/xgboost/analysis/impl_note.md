This note tracks the concrete implementation of the simplified XGBoost pipeline.

- Data is loaded via `load_config`, `load_raw`, `clean`, and `load_targets` in the notebook.
- Founder-level steps (the conceptual `xgboost_process`) are validated by tests under `xgboost/tests/test_xgboost_process_steps.py`.
- The tests assert the key shapes from the design:
  - 3.2.1: last founded company per founder from `founder_experience_training` → `(4772, 12)`.
  - 3.2.2: after joining `education_training` → `(4772, 14)`.
  - 3.2.3 + 3.2.3.1: after joining `company_info_training` and adding `founder_has_perf`, `founder_perf_mean`, `founder_perf_max`, `founder_perf_last` → `(4772, 20)`. The original doc stated 19 columns, but the natural schema is 12 (experience) + 2 (education) + 2 (company_info) + 4 (perf aggregates) = 20.
  - 3.2: after attaching `target_variable_training`, computing `label = floor(log1p(multiple))`, and removing founders whose last-founded company overlaps with inference → 4,769 founders with target metadata.
- `FeaturePipeline._select_last_company` was simplified to ignore rows with missing `company_id` before picking the last company, so we no longer lose founders whose final experience row lacks an ID.

These invariants keep the training code aligned with the design docs while staying simple: data shaping is done with plain pandas, model training stays in the notebook, and the library code only contains the minimal reusable pieces (config, loaders, features, and metrics).
