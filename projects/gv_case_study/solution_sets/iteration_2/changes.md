### instructions

If mode is `plan`:
-   Review the provided @task under given @context, write @analysis for the rootcause of the problem, and @fix_plan to resolve the problem. Add all relevant files to the @related_files section. Update this document at the end.

If mode is `execute`:
-   If the @fix_plan is not provided, ask the user for confirmation.
-   Execute the @fix_plan.

### context

The pipeline was Dropping 1198 rows with missing company_founded (25.12%).

However, in my initial analysis, I got

```
Below is training data analysis:

Number of real_founders: 4772
Number of companies they founded: 4937
Number of founders with at least one company in target_variable_training: 4772
Number of real founders with at least one company in target_variable_training and company_info: 4772
Number of founders in training after removing inference founders: 4769
Number of founders in training after removing founders associated with inference companies: 4769
```

This means my baseline approach of choosing only the last founded company for each founder is not a good idea.

The challenge I have is label construction.

**what I have**
- founder experience
- company info
- target_variable_training (exited multiples)

**what I need**
- A label for each founder that indicates the multiple they exited for the final company they founded.

**what I will do**

docs/xgboost/execution/issue_2025-11-23_21-46-14.md outline how the company in final founder_matrix is choosen (i.e using last founded company determined by order).

Since:
Each founder can have multiple experiences, where they are a founder (is_founder=True).
Only a subset of companies have multiples (exited).
Each founder have at least one company in their experience that appears in the target_variable_training.

Therefore:
A good label for founder rank, is the combined multiples of the companies that they founded that appears in the target_variable_training.
company_id is not a feature, but for simplcity, let's start this way:
For each founder, get the last company (ranked by `order` column) in their experience that appears in the target_variable_training.
This company's id, industry, company_founded, and multiple (exited) are used in the founder matrix.

After _prepare_split_frame from xgboost/src/data/splitters.py, I expect 4772 rows.

### task

update pipeline to reflect my changes.

### analysis
The drop of 1,198 rows during `_prepare_split_frame` was caused by how the
training dataset was constructed, not by the splitter itself.

In the original implementation of `build_training_dataset`:

- `FeaturePipeline.build_matrix` selected each founder’s **last founded company**
  purely by `order` in `founder_experience_training`.
- The training frame then left‑joined `target_variable_training` on this
  `company_id` to attach `company_founded` and `multiple`.

This created a mismatch with the assumptions in the context:

- Every founder has **at least one** founded company that appears in
  `target_variable_training`, but their **last founded company** is not always
  one of those labeled companies.
- For founders whose last company had no target row, the join produced
  `NaN` for `company_founded` and `multiple`. Later, `_prepare_split_frame`
  dropped these rows because it requires a valid `company_founded` to build
  per‑industry temporal splits.

So the root cause is: **labels were attached to whichever company happened to
be last in the experience history, instead of to the last company that
actually has a label.** That violates the intended design in this issue and
causes unnecessary loss of training founders.

There is a second, smaller source of missing `company_founded`: a handful of
companies in `target_variable_training.csv` themselves have a missing founding
year. Those rows cannot be fixed by the pipeline and represent true gaps in
the curated data. After the fix, only these few founders are missing
`company_founded`; the rest are preserved.

### fix_plan

1. **Derive label metadata from targets, not from the feature matrix**
   - Implement a helper in `src/models/training_pipeline.py` that:
     - Starts from `clean_training.experience` and `clean_training.company_info`.
     - Filters to founder rows (`is_founder=True`) with non‑null `company_id`.
     - Joins those experience rows with `target_variable_training` to keep only
       experiences whose `company_id` appears in the target table.
     - For each `person_id`, sorts by `order` and selects the **last labeled**
       company.
     - Attaches `industry`, `company_founded`, `multiple`, and `performance`
       for that company.
   - This yields a per‑founder metadata frame:
     `<person_id, label_company_id, label_industry, company_founded, multiple, label_performance>`.

2. **Attach label metadata to founder features by `person_id`**
   - Keep `FeaturePipeline.build_matrix` unchanged and label‑agnostic; it still
     produces one row per founder with aggregated features based on the last
     founded company and overall performance history.
   - In `build_training_dataset`, join the feature frame with the label metadata
     on `person_id` (not `company_id`) so there is exactly one row per founder.
   - After the join, override the feature frame’s `company_id`, `industry`,
     and `performance` with the label‑company values:
     - `company_id = label_company_id`
     - `industry = label_industry` (normalized, with `"unknown"`/missing
       mapped to `"Other"`)
     - `performance = label_performance`

3. **Compute labels from multiples for the last labeled company**
   - Use `multiple` from the label metadata to derive the integer relevance
     grade with the existing helper `calculate_relevance_grade`, and store it
     in `features.target_column` (currently `label`).
   - Drop the raw `multiple` column afterwards to keep the training frame clean.

4. **Keep leakage removal but base it on the labeled company**
   - Reuse the existing leakage logic that scans the ranking (inference)
     dataset, finds each inference founder’s last founded company, and builds
     the set of those `company_id` values.
   - Drop any training founder whose **labeled** `company_id` appears in that
     set. This preserves the intended “no overlap between training labels and
     inference last companies” constraint.

5. **Normalize `company_founded` and verify invariants via tests**
   - Continue coercing `company_founded` to numeric in
     `build_training_dataset`; `_prepare_split_frame` will still drop rows with
     missing founding years, but now these should only be the few companies
     whose founding year is missing in `target_variable_training` itself.
   - Extend `tests/models/test_training_dataset.py` to assert:
     - Every training `company_id` exists in the target table.
     - Any remaining `NaN` in `company_founded` correspond exactly to entries
       that are already missing in the target file (no extra missingness is
       introduced by the pipeline).

6. **Run targeted tests to confirm the behavior**
   - Run:
     - `pytest -q tests/models/test_training_dataset.py`
     - `pytest -q tests/features/test_pipeline_xgboost_process.py`
     - `pytest -q tests/test_xgboost_process_steps.py`
   - Confirm:
     - Training dataset has 4,769 founders as before (after leakage removal).
     - All training companies are drawn from `target_variable_training`.
     - Only a tiny number of founders lack `company_founded`, matching the
       gaps in the target data, so `_prepare_split_frame` no longer drops
       ~25% of the training set.

### related_files

- `xgboost/src/models/training_pipeline.py`
- `xgboost/tests/models/test_training_dataset.py`
- `xgboost/src/data/splitters.py`
- `xgboost/src/features/pipeline.py`
