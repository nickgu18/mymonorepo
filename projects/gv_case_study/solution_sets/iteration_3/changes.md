### instructions

If mode is `plan`:
-   Review the provided @task under given @context, write @analysis for the rootcause of the problem, and @fix_plan to resolve the problem. Add all relevant files to the @related_files section. Update this document at the end.

If mode is `execute`:
-   If the @fix_plan is not provided, ask the user for confirmation.
-   Execute the @fix_plan.

### context
/Users/yugu/Desktop/gehirn/gv_case_study/solution_sets/iteration_2/problems.md
### task

Create a revised solution with Train, validate, and test split.
Add the updated code in:
/Users/yugu/Desktop/gehirn/gv_case_study/xgboost/notebooks/GV_Exercise_Iteration3.ipynb

### analysis
In iteration 2 the pipeline only had a **train / test** split (per industry,
temporal), and we used the test set both for performance reporting and, in
practice, to reason about model quality. This has two main problems:

1. **No clean validation set for tuning**  
   - Any manual or automated hyperparameter search that looks at the test
     NDCG@20 is effectively tuning on the test set, which overstates general
     performance and makes later comparisons unreliable.
   - With only a single split, the NDCG estimates are also high‑variance for
     this small dataset (4,7xx founders), especially when per‑industry cohorts
     are imbalanced.

2. **Temporal label distribution shift is not explicitly controlled**  
   - The analysis in `iteration_2/problems.md` shows that test cohorts are
     dominated by Label 0, making the test task much easier than train and
     leading to the “Test NDCG >> Train NDCG” pattern.
   - This shift is a natural property of the data (newer companies haven’t
     exited yet), but with only train/test we have no middle slice (validation)
     to help us see how performance evolves over time and to choose
     hyperparameters without peeking at the very latest data.

Given the size of the dataset and the temporal nature of the problem, a
**three‑way temporal split per industry (Train / Validation / Test)** is the
right way to:

- Keep evaluation realistic (always training on older companies and predicting
  on newer ones).
- Reserve a held‑out test slice that is never touched during tuning.
- Use the validation slice to adjust model capacity, early stopping, and
  regularization so that we reduce underfitting on the harder, more diverse
  training cohorts without overfitting to the specific test period.

### fix_plan

1. **Design a per‑industry temporal 3‑way splitter**
   - Implement a helper (either in `src/data/splitters.py` or directly in the
     notebook) that:
     - For each industry:
       - Sorts by `company_founded` ascending.
       - Cuts the series into three contiguous segments by ratio, e.g.
         70% Train, 15% Validation, 15% Test.
     - Returns concatenated `train_df`, `val_df`, `test_df` plus group counts
       per industry:
       - `train_groups`, `val_groups`, `test_groups`
       - `industry_names` (consistent order across groups).
   - Keep the splitter logic simple and deterministic (no shuffling), so that
     the notebook can easily report per‑industry counts and label distributions
     for all three splits.

2. **Integrate the 3‑way split into `GV_Exercise_Iteration3.ipynb`**
   - Reuse the existing training dataset builder:
     - `training_df = build_training_dataset(clean_training, clean_ranking, target_df, cfg.features)`
   - Apply the new temporal splitter:
     - Produce `train_df`, `val_df`, `test_df` and corresponding
       group vectors.
   - Derive matrices and labels:
     - `feature_columns = cfg.features.selected_columns`
     - `X_train, y_train` from `train_df[feature_columns]`, `train_df[label]`
     - `X_val, y_val` from `val_df[feature_columns]`, `val_df[label]`
     - `X_test, y_test` from `test_df[feature_columns]`, `test_df[label]`
   - Print a concise split summary in the notebook:
     - Total rows and per‑split counts.
     - Per‑industry label histograms for Train / Val / Test, mirroring the
       existing `_print_split_summary` style but extended to three splits.

3. **Train with Train / Validation; reserve Test strictly for final eval**
   - In `GV_Exercise_Iteration3.ipynb`:
     - Instantiate `XGBRanker` with current hyperparameters.
     - Use `eval_set=[(X_train, y_train), (X_val, y_val)]` and
       `eval_group=[train_groups, val_groups]` so early stopping, if enabled,
       uses the validation slice.
     - For any future hyperparameter tuning (manual or automated), restrict
       evaluation to Train/Validation only and keep Test untouched.
   - After parameters are chosen:
     - Option A (simpler): keep the best model from the Train/Val run and
       evaluate it on Test.
     - Option B (slightly more complex): retrain on Train+Validation with the
       chosen parameters, then evaluate on Test.
   - Log and print NDCG@20:
     - On Train, Validation, and Test overall.
     - Per industry for each split (Train/Val/Test) using existing NDCG
       helpers in `src/models/metrics.py` where convenient.

4. **Add a test for the splitter**
   - If the splitter is implemented in `src/data/splitters.py`, add a focused
     unit test under `xgboost/tests/data/` that:
       - Calls the new function on the real training frame.
       - Asserts:
         - `len(train_df) + len(val_df) + len(test_df)` equals the
           input length.
         - Group counts match per‑industry totals.
         - Within each industry, `company_founded` is non‑decreasing across
           Train → Val → Test.

### related_files

- `solution_sets/iteration_2/problems.md`
- `xgboost/notebooks/GV_Exercise_Iteration3.ipynb`
- `xgboost/src/data/splitters.py`
- `xgboost/src/models/training.py`
- `xgboost/src/models/metrics.py`
- `xgboost/src/models/training_pipeline.py`
