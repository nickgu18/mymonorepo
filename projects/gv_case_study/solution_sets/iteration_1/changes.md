### instructions

If mode is `plan`:

- Review the provided @task under given @context, write @analysis for the rootcause of the problem, and @fix_plan to resolve the problem. Add all relevant files to the @related_files section. Update this document at the end.

If mode is `execute`:

- If the @fix_plan is not provided, ask the user for confirmation.
- Execute the @fix_plan.

### context

**docs**
docs/xgboost/analysis
docs/xgboost/analysis/questions
docs/xgboost/analysis/train_thought.md
xgboost/notebooks/data_analysis.ipynb

**code**
xgboost/src
xgboost/configs
xgboost/notebooks/GV_Exercise_Simple.ipynb

### task

Some key points to note:

- Training data has overlap with inference data, founders who have at least one founded comapny in training data (target_variable_training, company_info_training) should be removed.
- Split should be done per industry.
- Multiples are going to serve as the grade for XGBoost, and since the original value is highly skewed, I need to apply a log1p transform to it. np.log1p(x)=ln(1+x), so it will be 0 for 0 and 1 for 1, and then it will be a smooth curve for larger values
- there are many additional features that can be developed, but I'm going to start with the basic set of features.

**xgboost_process**

1. Load Data (training, inference and target_variable_training)
2. Clean Data
   2.1 Patch default values for founder_experience
3. Build Matrix: Goal is to create a founder_matrix of {<person_id, features, company_id>, metadata(industry, company_founded, floor(log1p(multiple)))} for training
  3.1 Creating <person_id, features, company_id>
    3.2.1 Start with founder_experience table, filter all founders with is_founder=true, get last company (determined by order) they founded
      - expected shape: (4772, 12)
    3.2.2 combine education_training
      - expected shape:(4772, 14)
    3.2.3 combine company_info (leave performance as is). additional features to add include `founder_has_perf`
      - expected shape: (4772, 17)
      3.2.3.1 Compute aggregated performance features:
        - `founder_perf_mean` = mean of `performance` over founded companies (NaN if none).
        - `founder_perf_max` = max of `performance` over founded companies (NaN if none).
        - `founder_perf_last` = last `performance` value over founded companies (NaN if none).
        - expected shape: (4772, 20)
  3.2 combine target_variable_training (same treatment for performance), remove companies that appeared in inference (founder's last company). this step adds the metadata {company_founded, floor(log1p(multiple))}
    - expected shape: (4769, 22)
4. Split Train and Test per industry
   1. validate number of founders per industry, before and after split
   2. validate founder label distribution per industry, before and after split (I want to know label distrubiton for train and test per industry)
5. Train ranker using industry as group
6. Run model on inference data per industry

**task**
A.Plan how how this proposed simple solution can be implemented by **significnatly reducing** code complexity of my existing code in xgboost/src.

B. Move these features (    - direct_network_size
    - indirect_network_size
    - network_quality
    - team_size) to xgboost/src/features/feature_factory.py, and remove them from xgboost/src/features/pipeline.py.
    - Test: Each feature addition still works.
    - Test: Final founder feature matrix after step 3.2.3.1 still has shape (4772,20)

**Success_Criteria:**
Entire pipeline implementation is planned, actual training, inference and generating final explanation is done in GV_Exercise_Simple.ipynb.
Complex code structure and functions are simplified greatly, keeping only those support initial training, still with proper SWE architectire and MLOps considerations.
All of these considerations, and why these things were done, should be stored in docs/xgboost/analysis/impl_note.md

### analysis

Root cause is that the current XGBoost implementation under `xgboost/src` has grown around a richer, highly modular architecture (separate data, features, models, predict layers plus MLflow wiring), while the “simple first run” you want is still only encoded in notebooks and design docs. The core ideas from `train_thought.md`—founder‑level matrix, log1p(multiple) grades, per‑industry splits, and explicit leakage removal—exist as scattered utilities (`FeaturePipeline`, `calculate_relevance_grade`, `split_by_industry`, `train_ranker`) and analysis notebooks, but there is no single, minimal training pipeline that:

- Builds the founder_matrix directly from the curated CSVs, attaches MOIC‑based labels, and filters to “true founders of target companies”.
- Explicitly removes founders whose founded companies overlap between training and inference populations (the 4,772 → 4,769 adjustment), and asserts this invariant in code.
- Splits the labeled founders per industry (and time) into `X_train`, `y_train`, `X_test`, `y_test` plus `group` vectors for `rank:ndcg`, then calls `train_ranker` with those groups.
- Is simple enough to be the canonical reference for GV_Exercise_Simple.ipynb, so the notebook just calls “load → build_training_dataset → train_ranker → predict_batch” instead of re‑implementing glue logic.

Because these responsibilities are currently spread across notebooks, tests, and several modules, the codebase feels heavier than necessary for an initial XGBoost ranker, and key behaviors (leakage removal, label construction, cohort grouping) are not owned by a single, easy‑to‑read pipeline function. The planning task is therefore to carve out a slim, founder‑centric training/inference path that reuses the good building blocks but hides unnecessary complexity behind a small number of well‑named helpers and a simplified notebook.

### fix_plan

1. **Step 1 – Load data (training, inference, target_variable_training)** [correct]

   - Keep all file I/O in `GV_Exercise_Simple.ipynb` (no loading inside `build_training_dataset`):
     - Import `load_config`, `load_raw`, `clean`, and `load_targets`.
     - Load config once: `cfg = load_config("configs/base.yaml")`.
     - Training data:
       - `raw_training = load_raw(cfg.data, dataset="training")`
       - `clean_training = clean(raw_training)`
     - Inference / ranking data:
       - `raw_ranking = load_raw(cfg.data, dataset="ranking")`
       - `clean_ranking = clean(raw_ranking)`
     - Training targets:
       - `target_df = load_targets(cfg.data)` to load `target_variable_training.csv`.
   - Stop using the `load_and_clean` convenience wrapper from notebooks; always call `load_raw` then `clean` explicitly.

2. **Step 2 – Clean data (including patching founder_experience defaults)** [correct]

   - Keep `src/data.loaders.clean` focused on generic cleaning:
     - Normalize IDs with `normalize_ids`.
     - Parse dates via `parse_dates`.
    - Convert `company_info.performance` to numeric (preserve NaN; no median computation).
   - Implement “patch default values for founder_experience” in the feature pipeline:
     - Refactor `FeaturePipeline._build_founder_features` into helper `_prepare_experience_and_founders(clean_data)` that:
       - Copies `clean_data.experience`.
       - Ensures boolean columns `is_founder`, `is_executive`, and `is_c_suite` exist and are filled with `False` where missing (or non‑truthy), so downstream logic always sees well‑defined booleans.
       - Parses `start_date` / `end_date` to timestamps (using the same conversion as `clean`) and computes `exit_moic = company_id.map(outcome_lookup)`.
       - Handles empty/zero‑founder cases by returning an empty founder frame via `_empty_founder_frame()`.

3. **Step 3 – Build founder matrix for training (per founder‑company rows + labels)**

 3.1 **Founder features (simplified)**

  - Use `FeaturePipeline.build_matrix(clean_training)` to construct a founder‑level matrix with one row per founder representing their last founded company.

    - Returns **one row per `person_id`** (with attached `company_id` for the last founded company) and `metadata.entity_column = "person_id"`.
    - Includes identifiers (`person_id`, `company_id`) and configured feature columns. Metadata column `industry` is present; `company_founded` is attached later in Step 3.2 from `target_variable_training.csv` for training (and may be absent for ranking).

  - Implementation details mapped to existing code and simplified behavior:

    - [x] Input contract: `RankingCleanData` with normalized `experience`, `education`, `company_info` (`xgboost/src/data/types.py:20–27`).

    - [x] Real founders and last company:
      - Identify founders as persons with any `is_founder == True` in `experience` (`xgboost/src/features/pipeline.py:104–119`).
      - Determine each founder’s last founded company by the `order` column from `founder_experience_training.csv` (descending per person); if `order` is missing, fall back to the latest `start_date` in `experience`.
      - Build a `founder_current` frame of (`person_id`, `company_id`) for this last company.

    - [x] Education merge:
      - Merge `founder_current` with `education` to bring `education_tier` and `highest_level`.
      - Map `highest_level` to `education_level_score` via `_score_degree` (`xgboost/src/features/pipeline.py:299–305`).

    - [x] Company merge:
      - Merge `founder_current` with `company_info` to attach `industry` and `performance` for the last company. Do not attach `company_founded` here; it is sourced from `target_variable_training.csv` in Step 3.2 (training only).

    - [x] Task B – move network/team features out of the core pipeline:
      - Implement `xgboost/src/features/feature_factory.py` with small, pure helpers that own the logic for:
        - building the co‑worker adjacency graph from `experience`,
        - computing `direct_network_size` / `indirect_network_size`,
        - computing `network_quality`,
        - computing `team_size` for the last founded company.
      - Keep `FeaturePipeline` focused on the minimal feature set for the initial ranker:
        - `performance`, `education_tier`, `education_level_score`,
        - `founder_has_perf`, `founder_perf_mean`, `founder_perf_max`, `founder_perf_last`,
        - plus IDs/metadata (`person_id`, `company_id`, `industry`, `is_founder_of_target`).
      - Do not wire network/team features into `FeaturePipeline.build_matrix` for now; they can be added later by calling `feature_factory` explicitly from notebooks or a future richer pipeline.
      - Add tests:
        - `tests/features/test_feature_factory.py` to verify each helper on both real data and a tiny synthetic example.
        - `tests/features/test_pipeline_xgboost_process.py` to assert that the founder feature matrix after step 3.2.3.1 has 4,772 rows and includes the simplified spec columns (IDs, `performance`, education features, and `founder_*perf*` aggregates).

    - [x] Founder performance features:
      - Aggregate `company_info.performance` over all founded companies for each founder to compute:
        - `founder_has_perf` (any performance available), `founder_perf_mean`, `founder_perf_max`, `founder_perf_last` (by `company_founded` or latest `start_date`).
      - Include only if present in `cfg.features.selected_columns` (`xgboost/src/common/config.py`).

    - [x] Omitted complexity:
      - No `t0_date` or 5‑year velocity windows; no prior role filtering; no exec flags.
      - No `tiered_exit_*` bins from `exit_moic`.
      - No `company_founded_lookup` or fallback logic beyond using `company_info.company_founded` (rows with missing founding year will be dropped during splitting).

  - Refactor plan: break down `FeaturePipeline.build_matrix` for readability and alignment with simplified behavior

    - [x] Orchestrator (`build_matrix`) – `xgboost/src/features/pipeline.py:75–95`
      - Drives the helper sequence below, constructs `FeatureMetadata` using only configured feature columns, and returns a `FeatureMatrix` with `person_id` as the entity.
      - Ensures metadata columns such as `industry` are present but excluded from `feature_columns`; `company_founded` is attached later in Step 3.2 via `build_training_dataset`.

    - [x] `_prepare_experience(clean_data)` – normalize booleans and dates – `xgboost/src/features/pipeline.py:104–113`
      - Inputs: `clean_data.experience`
      - Outputs: `experience` with patched `is_founder`, `is_executive`, `is_c_suite`, and parsed `start_date`/`end_date`.

    - [x] `_identify_real_founders(experience)` – select founders and histories – `xgboost/src/features/pipeline.py:114–119`
      - Outputs: `founder_ids`, `founder_history` filtered to founders.

    - [x] `_select_last_company(founder_history)` – last founded company per founder
      - Prefer the highest `order` value per founder (as in `founder_experience_training.csv`); if `order` is unavailable, fall back to the latest `start_date` in `founder_history`. Ignore rows with missing `company_id` when choosing the last company, so no founders are dropped due to null IDs.
      - Outputs: `founder_current` with (`person_id`, `company_id`).

    - [x] `_merge_education(founder_current, education)` – education features – `xgboost/src/features/pipeline.py:136–148`
      - Adds `education_tier` and maps `highest_level` → `education_level_score` via `_score_degree` – `xgboost/src/features/pipeline.py:299–305`.

    - [x] `_merge_company_context(founder_current, company_info)` – company metadata
      - Attaches `industry` and `performance` via direct merges – `xgboost/src/features/pipeline.py:120–129`.

    - [x] `_aggregate_founder_performance(founder_history, company_info)` – perf aggregates
      - Calculates `founder_has_perf`, `founder_perf_mean`, `founder_perf_max`, `founder_perf_last` (by latest `start_date` or by `company_founded` once training targets are joined).
      - Only included if configured in `cfg.features.selected_columns` – `xgboost/src/common/config.py`.

    - [x] `_assemble_founder_rows(founder_current, merges, network_maps, team_size_map)` – row assembly
      - Emits one row per founder with identifiers, metadata, and the simplified feature set – mirrors `xgboost/src/features/pipeline.py:244–264`.
      - Provides `_empty_founder_frame` for no‑data cases – `xgboost/src/features/pipeline.py:277–288`.

  3.2 **Join targets, derive labels, remove leakage**

  - Implement `build_training_dataset(clean_training, clean_ranking, target_df, feature_cfg)` in `src/models/training_pipeline.py` (implemented):
    - Build simplified founder rows via `FeaturePipeline(feature_cfg).build_matrix(clean_training)` (one row per founder: last founded company).
    - Join `target_df` (`target_variable_training.csv`) on `company_id` to attach target metadata:
      - Bring `company_founded`, `multiple`, and `industry` from `target_df`.
      - Industry correction: if founder matrix `industry == "Other"` and `target_df.industry` is present and not `Other`, set `industry = target_df.industry`.
    - Derive integer labels using `calculate_relevance_grade(multiple)` (`floor(log1p(multiple))`, 0 for missing/≤0) from the last company, and drop the raw `multiple` column after label construction.
    - Leakage removal using the ranking dataset:
      - For `clean_ranking`, identify each founder’s last founded company and construct the set of last-founded `company_id` values.
      - Drop any training founder whose last founded `company_id` appears in this set (matching the “remove companies that appeared in inference (founder’s last company)” rule from `xgboost_process`).
    - Coerce `company_founded` to numeric in `build_training_dataset`; downstream splitters are responsible for dropping rows with missing founding year.
    - Final training frame: **one row per founder** with `person_id`, `company_id` (last), `industry`, `company_founded` (metadata), simplified feature columns, and `label`. Current implementation on the real data yields 4,769 rows after leakage removal, as asserted in `tests/models/test_training_dataset.py`.

1. **Step 4 – Split train/test per industry**

  - In `GV_Exercise_Simple.ipynb`, after `train_df = build_training_dataset(...)`:
    - Select `feature_columns` from `cfg.features.selected_columns`.
    - Call `split_by_industry(train_df, feature_columns, target_col="label", train_ratio=0.8)` from `src.data.splitters` to obtain:
      - `X_train`, `y_train`, `X_test`, `y_test`,
      - `train_df`, `test_df`,
      - `train_groups`, `test_groups`, `industry_names`.
    - Behavior (matching the xgboost_process ask “Split Train and Test per industry”):
      - Each industry is treated as its own cohort and split independently.
      - Within each industry, rows are sorted by `company_founded` (oldest first), and an 80/20 temporal split is applied:
        - training set contains older companies,
        - test set contains newer companies.
      - Rows with missing `company_founded` are dropped inside `split_by_industry` before splitting, so temporal ordering is well‑defined.
      - The returned `train_groups` / `test_groups` and `industry_names` can be passed directly to `train_ranker` as group arrays for XGBRanker (one group per industry).

5. **Step 5 – Train ranker using industry groups**

  - [x] Fit `XGBRanker` with group arrays from the split using `src.models.training.train_ranker`:
    - In `GV_Exercise_Simple.ipynb`:
      ```python
      params = cfg.model.hyperparameters.copy()
      ranker, metrics = train_ranker(
          X_train=X_train,
          y_train=y_train,
          X_test=X_test,
          y_test=y_test,
          train_groups=train_groups,
          test_groups=test_groups,
          industry_names=industry_names,
          params=params,
          tracking_uri=cfg.tracking.uri,
          experiment_name=cfg.tracking.experiment_name,
          run_name=datetime.now(timezone.utc).strftime(\"%Y%m%dT%H%M%SZ\"),
      )
      ```
    - `train_ranker`:
      - logs hyperparameters and basic dataset stats to MLflow,
      - trains a single `XGBRanker` with per‑industry group arrays (`train_groups`, `test_groups`),
      - logs a global training label histogram and a top‑K feature importance bar plot,
      - computes per‑group NDCG on train/test, logs macro NDCG, and prints per‑industry scores using `industry_names`.

6. **Step 6 – Run model on inference data per industry**

  - [x] Reuse `clean_ranking` loaded earlier in the notebook.
  - [x] Build ranking features with the same feature configuration:
    - In `GV_Exercise_Simple.ipynb`:
      ```python
      from src.features.pipeline import FeaturePipeline

      raw_ranking = load_raw(cfg.data, dataset=\"ranking\")
      clean_ranking = clean(raw_ranking)

      feature_pipeline = FeaturePipeline(cfg.features)
      ranking_features = feature_pipeline.build_matrix(clean_ranking)
      ```
  - [x] Load the trained bundle and score founders:
    - Persist the trained model and feature column list under a timestamped `notebook_runs/<run_name>` directory:
      ```python
      run_dir = cfg.model.artifact_dir / \"notebook_runs\" / run_name
      run_dir.mkdir(parents=True, exist_ok=True)
      model_path = run_dir / \"ranker.json\"
      artifacts_path = run_dir / \"artifacts.json\"
      ranker.save_model(model_path)
      artifacts = {\"feature_columns\": feature_columns}
      artifacts_path.write_text(json.dumps(artifacts, indent=2))
      ```
    - Reload the bundle via `load_model_bundle` and run batch prediction with SHAP explanations:
      ```python
      bundle = load_model_bundle(
          registry_cfg=cfg.registry,
          project_root=cfg.project.root,
          model_root=run_dir,
      )
      predictions = predict_batch(bundle, ranking_features, shap_top_n=3)
      ```
    - `predict_batch`:
      - selects the trained feature columns from `ranking_features`,
      - computes scores and ranks per founder,
      - optionally computes SHAP explanations for each prediction via `summarize_shap`,
      - returns a frame ordered by `rank` with columns such as `founder_id`, `industry`, `score`, `rank`, `explanation` (and `company_founded` when available).
  - [x] Compute per‑industry SHAP summaries in the notebook (Phase 8):
    - Use `shap.TreeExplainer(bundle.estimator)` and `ranking_features.select_columns(bundle.feature_columns)` to:
      - log global SHAP summary plots (bar and beeswarm),
      - iterate over industries and render per‑industry SHAP summaries (excluding `unknown`), providing a per‑industry explanation of feature impact at inference time.

7. **Cross‑cutting refactors, removals, and documentation**

   - Execute the simplifications already planned:
     - Remove `company_founded_lookup` plumbing and `build_company_founded_lookup` so `build_matrix` remains fully label‑agnostic, and `company_founded` is sourced only from `target_variable_training.csv` via `build_training_dataset`.
     - Stop using `load_and_clean` in notebooks; call `load_raw` + `clean` explicitly.
     - Remove `FeaturePipeline.impute_field` from the public contract and rely on NaNs + XGBoost’s native missing‑value handling.
     - Treat advanced network helpers as internal-only until the simple path is stable.
     - Remove `perf_median` from `RankingCleanData` and stop computing it in `src/data/loaders.clean`; models will rely on native missing‑value handling for `performance`.
     - Remove time‑window and exit‑bin features from `FeaturePipeline._build_founder_features` (no `t0_date`, `role_velocity_5yr`, `exec_role_5yr`, `tiered_exit_*`). Keep only the simple merges, education mapping, `performance`, and the perf aggregates in the core path; treat network/team features as optional extras implemented in `feature_factory` rather than part of the main pipeline.
     - Simplify `split_by_industry` to deterministic year‑based splitting:
       - Signature: `split_by_industry(df, feature_cols, target_col, cutoff_year_map: dict[str, int] | int)`.
       - For each industry, train = rows with `company_founded <= cutoff`, test = rows with `company_founded > cutoff`.
       - Return `X_train`, `y_train`, `X_test`, `y_test`, `train_df`, `test_df`, `train_groups`, `test_groups`, `industry_names` with minimal side effects (no verbose printing unless `debug=True`).
   - Documentation and tests:
     - Capture the “before vs after” architecture and the rationale (SIMPLE principle, per‑industry NDCG, leakage avoidance, log1p labels) in `docs/xgboost/analysis/impl_note.md`.
     - Add focused tests for:
       - `build_training_dataset` (correct log1p label construction and 4,772 → 4,769 leakage removal).
       - The refactored `_prepare_experience_and_founders` / `_build_founder_company_row` helpers (ensuring they emit founder‑level rows and features matching your design).

### companion_view (HTML)

See `docs/xgboost/execution/compainion.html` for a side‑by‑side HTML view of current vs. new/simple functions by directory.

### related_files

- docs/xgboost/analysis/train_thought.md
- docs/xgboost/analysis/questions/how_to_handle_multiple_for_xgboost.md
- docs/xgboost/analysis/questions/what_happens_with_overlapping_industries.md
- docs/xgboost/analysis/questions/performance_coverage_for_founded_companies.md
- docs/xgboost/analysis/questions/how_to_impute_performance_for_missing_founders.md
- docs/xgboost/analysis/impl_note.md
- xgboost/configs/base.yaml
- xgboost/src/common/config.py
- xgboost/src/data/loaders.py
- xgboost/src/data/analysis.py
- xgboost/src/data/splitters.py
- xgboost/src/models/training_pipeline.py
- xgboost/src/features/pipeline.py
- xgboost/src/features/**init**.py
- xgboost/src/models/metrics.py
- xgboost/src/models/training.py
- xgboost/src/models/types.py
- xgboost/src/predict/inference.py
- xgboost/notebooks/GV_Exercise_Simple.ipynb
- xgboost/notebooks/GV_AutoML.ipynb
- xgboost/notebooks/output.md
- xgboost/tests/data/test_analysis.py
- xgboost/tests/data/test_splitters.py
- xgboost/tests/data/test_outcome_unification.py
- xgboost/tests/features/test_pipeline.py
- xgboost/tests/features/test_t0_filter.py
- xgboost/tests/models/test_training_population.py
- xgboost/tests/models/test_metrics.py
