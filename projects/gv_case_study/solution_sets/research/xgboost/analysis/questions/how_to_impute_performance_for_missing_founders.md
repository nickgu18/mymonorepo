success criteria of answers: comprehensive, and also include a ELI5 section for beginners.

Question:

Building on the performance coverage analysis: how should I impute `performance` for founders who have no performance for any of their founded companies, given that around 88% of founders in training have at least one `performance` value but only ~40% of founders in inference do?

Analysis:

- Data situation:

  - Training founders: about **88%** have `performance` for at least one founded company; ~11–12% have none.
  - Inference founders: about **40%** have `performance` for at least one founded company; ~60% have none.
  - So `performance` is a strong but **sparsely observed** signal, especially at inference time.

- What happens if I impute only in training and not in inference?

  - Assume we fill missing `performance` in training with an industry median or global mean, but leave inference founders’ missing values as `NaN`.
  - **During training**:
    - The `performance` feature has **no NaNs**, because everything was imputed.
    - Trees see a fully observed numeric feature and learn splits like `performance < 2.3`, assuming every row has a value.
    - Founders who originally had no performance are treated as “average‑performance founders,” and the model never learns that “no performance info” is its own pattern.
  - **During inference**:
    - Some founders have real numeric `performance`; others have `NaN`.
    - For a split like `performance < 2.3`, XGBoost routes **NaNs down the default branch**, which was chosen during training when there were _no_ missing values.
    - All “no‑performance” founders at inference are forced through default branches the model never truly optimized for the “missing perf” case.
  - Downsides:
    - **Train/serve skew:** The training distribution (no missing perf) differs from the inference distribution (many missing perf), so offline metrics are optimistic relative to reality.
    - **Lost missingness signal:** Missing `performance` is actually informative (“we don’t have any tracked outcome for this founder’s companies”), but imputation in training hides this signal.
    - **Unconstrained behavior on NaNs:** Default branches for `performance` splits are effectively arbitrary for missing cases, because training never had to optimize for them.
    - **Harder debugging:** Evaluation pipelines that mirror the _training_ imputation will look clean, while production inference (no imputation) silently behaves differently.

- Best practice with XGBoost in this setup:

  - **Do not impute `performance` at all** for this feature; instead:
    - Keep `performance` as `NaN` whenever it is truly missing, in both training and inference.
    - Add a separate binary feature, e.g. `founder_has_perf` or `has_any_founded_company_perf`, which is:
      - `1` if the founder has at least one founded company with non-null `performance`.
      - `0` if they have none.
    - Optionally, compute aggregate performance features only when available, e.g.:
      - `founder_perf_mean` = mean of `performance` over founded companies (NaN if none).
      - `founder_perf_max` or `founder_perf_last` similarly defined.
  - XGBoost naturally handles NaNs:
    - At each split, it learns a “default” direction for NaNs _based on training data that actually contains NaNs_.
    - Because missingness appears in both training and inference, the model can learn separate behavior for “has performance” vs “no performance” founders using both the numeric value and the boolean flag.

- If you really want numeric imputation:
  - Treat imputation as part of the **feature pipeline**, not a training‑only trick:
    - Apply the exact same imputation rule (e.g., industry median) to both training and inference.
    - Always keep a `has_perf` indicator so the model knows which rows were imputed.
  - Even then, for XGBoost specifically, this is usually **not** better than leaving NaNs and modeling missingness explicitly, because trees already support NaNs natively.
  - What happens if I impute **both** training and inference with a median value?
    - Setup:
      - Suppose you replace every missing `performance` with an industry‑level median (or global median) in **both** training and inference.
      - Optionally, you also keep a `has_perf` flag (1 = had at least one real perf value, 0 = everything was imputed).
    - During training:
      - The `performance` feature has **no NaNs**; XGBoost never uses its special missing‑value routing for this column.
      - Founders with real `performance` keep their numeric values; founders with no performance all share the same imputed median value.
      - Trees learn splits like `performance < 2.3`; founders with imputed values land on one side of these thresholds purely based on that median, not because they actually had average performance.
      - If you _do_ include `has_perf`, the model can still detect “this founder was imputed” vs “this founder had a real performance,” but it has to learn that from the flag, not from NaNs.
    - During inference:
      - The distribution of `performance` is consistent with training: no NaNs, same median‑imputation rule.
      - There is **no train/serve skew in the handling of missingness**; the model sees the same kind of input it was trained on.
      - However, the **proportion** of imputed founders differs (≈12% in training vs ≈60% in inference), so:
        - The feature’s empirical distribution shifts toward the median at inference.
        - Many more founders cluster around the median `performance` value, so the model’s ranking for them relies heavily on other features and the `has_perf` flag (if present).
    - Pros:
      - No NaNs to worry about; some tooling prefers this.
      - No inconsistent treatment of missing values between training and inference (no train/serve skew from imputation itself).
      - If you keep a `has_perf` flag, the model can still treat “no performance” founders differently.
    - Cons (compared to leaving NaNs):
      - You **hide the natural missingness** in the numeric column itself; all missing founders look like “median performance” numerically, which can blur distinctions.
      - XGBoost’s native missing‑value handling is not used; instead you’ve encoded missingness via a separate flag and a hard-coded value.
      - When many inference founders are missing (60%), you create a large spike at the median, which can make the `performance` feature less expressive than a NaN‑aware approach.
      - If you forget the `has_perf` flag, the model cannot tell truly average founders from “unknown performance” founders.

ELI5:

- Imagine `performance` is a test grade for each company a founder built.
  - Some founders have grades for some companies; some have no grades at all.
- If you “guess” grades for missing ones **only when you train** the model, you’re telling it:
  - “Pretend everyone had a grade; missing grades don’t exist.”
  - The model then learns patterns assuming all students have grades.
- Later, at inference time, you suddenly send it real missing grades again.
  - Now the model sees a situation it never practiced on—students with no grades—but it still has to make a decision.
  - It falls back to default paths that weren’t tuned for this “no grade” case.
- A better approach:
  - Don’t guess grades at all; leave them blank (`NaN`).
  - Add a simple flag: “does this founder have any graded company: yes/no?”
  - Let the model learn how to treat founders with grades differently from those without, using its built‑in ability to handle blanks.

Conclusion:

- With your current setup (XGBoost ranker, 88% coverage in training, 40% in inference), the safest and simplest strategy is:
  - **Do not impute `performance` for founders who lack it.**
  - Keep `NaN` in both training and inference, and add a boolean feature that says whether the founder has any founded company with recorded `performance`.
  - Optionally derive aggregate features (mean/last/max performance) that are also `NaN` when no performance exists.
- Imputing only during training but not during inference introduces train/serve skew, hides missingness as a signal, and yields less reliable behavior for the large group of inference founders who truly have no performance data.
- If you ever decide to impute numerically (e.g., median imputation), you must:
  - Apply the same imputation in both training and inference, and
  - Keep an explicit “was imputed” / “has performance” flag so the model can still learn that “unknown performance” is different from “truly average performance.”
- Given XGBoost’s native handling of `NaN`s, **no-imputation plus a missingness indicator** remains the recommended approach; median‑imputation for both train and inference is workable but usually a step down in expressiveness and signal fidelity for this feature.
