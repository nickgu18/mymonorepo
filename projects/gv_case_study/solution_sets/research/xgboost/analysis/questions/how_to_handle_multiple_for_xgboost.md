success criteria of answers: comprehensive, and also include a ELI5 section for beginners.

Question:

How should I handle the `multiple` column from `target_variable_training.csv` when training an XGBoost LambdaMART ranker? In particular, given the raw MOIC range (0.0–2957.5) and the log1p range (~0.0–8.0), what is the right way to transform `multiple` into labels for NDCG / LambdaMART? Also, given that all 4,772 (4,769 after leakage removal) training founders have at least one founded company with a `multiple`, do I need to unify with `performance` at all—and should I further bin `log1p(multiple)` into 0.5-width bins before creating relevance grades?

Analysis:

- Context and constraints:

  - `multiple` is MOIC (Multiple on Invested Capital), i.e. `$returned / $invested`.
  - The distribution is extremely skewed:
    - Many companies at 0–3x, a long tail of outliers up to ~2957x.
    - `log1p(multiple)` compresses this to roughly [0, 8].
  - XGBoost’s `rank:ndcg` / LambdaMART objective expects **non‑negative relevance degrees** per item (often integers), and optimizes ranking within each query group.
  - You ultimately care about ranking **founders**, not companies, so company‑level multiples must be projected into founder‑level labels.

- High‑level handling of `multiple` in **this dataset**:

  - 1. **Use `multiple` only (no unification needed for training founders)**:
    - From your earlier analysis:
      - All 4,772 training founders (4,769 after removing leakage) have at least one founded company with a `multiple` in `target_variable_training.csv`.
      - So every training founder can get a label from `multiple` alone; you do **not** need `performance` to create relevance degrees for founders.
    - A simple, dataset‑aligned strategy is:
      - For each company, use `multiple` as its outcome (ignore `performance` for label construction).
      - For each founder, aggregate their founded companies’ multiples into a single scalar (see step 3 below).
    - `performance` remains purely a **feature**, not part of the label.
    - Note: the more general `unified_outcome = multiple if notna else performance` pattern in `test_outcome_unification.py` is still useful if you ever train on entities that lack `multiple` but have `performance`. It is just not needed for your current founder training population.
  - 2. **Map `multiple` (or a founder‑level aggregate of it) to a relevance grade**:
    - Use the existing helper `src/models/metrics.py::calculate_relevance_grade`:
      - For `moic` (here, a company’s `multiple` or a founder‑level aggregate of multiples):
        - If `moic` is missing or ≤ 0: grade = 0.
        - Else: grade = `floor(log1p(moic))`, returned as an `int`.
      - Given your empirical log1p range (~0–8), this yields labels in `{0, 1, …, 7}`:
        - 0: ≤ 0× (no return / loss).
        - 1: small positive outcomes (≈1–e²−1 range at the company level).
        - …
        - 7: extreme outliers (dozens to thousands of multiples).
    - This approach:
      - Keeps labels **monotonic in MOIC** (higher multiples → higher grade).
      - Compresses the huge numeric range while preserving the fact that 10× is meaningfully better than 3×, and 100×+ is in a special “top” bucket.
      - Produces integer grades compatible with NDCG’s gain term `2^rel − 1`.
      - 3. **Project company outcomes to founder labels**:
    - For each founder, you need a single label representing their historical “best outcome”:
      - Join founder‑company rows from the feature matrix with the company‑level `multiple`.
      - For each founder:
        - Aggregate to a scalar outcome like:
          - `founder_outcome = max(multiple for all companies they founded)`.
          - This matches the design intent: we care most about the **best** multiple a founder has produced, not their average.
        - Apply the same transform:
          - `founder_label = calculate_relevance_grade(founder_outcome)`.
      - Attach `founder_label` as the target column (e.g. `relevance_grade`) for the LambdaMART model.
    - Alternative aggregations (less aligned with “fund returner” intuition):
      - Mean or median of multiples: tends to down‑weight rare outlier wins and make serial, moderate exits look similar to a single mega‑hit.
      - Sum of multiples: risks conflating “lots of small exits” with “one huge fund‑returner,” which is not what investors want prioritized.
  - 4. **Use the grades directly as NDCG labels**:
    - For each query group (e.g. `(industry, founded_year)` cohort of founders), you pass:
      - `y = founder_label` (0–7 integer).
      - `group` sizes = number of founders per cohort.
    - XGBoost’s LambdaMART objective treats these labels as relevance degrees:
      - Differences between 0 vs 1 vs 2 matter, but the model mainly optimizes relative ordering so long as label order is consistent.

- Why not use raw `multiple` as the label?

  - Heavy tail: A few 100×–1000× exits dominate the loss signal; the model focuses too much on explaining very rare cases.
  - Numerical instability: Extremely large labels can interact badly with the NDCG gain term if you directly plug them into gain functions.
  - Hard to interpret: Explaining “why the model prefers 2957× over 300×” is less meaningful than a simpler “high vs medium vs low” grade.

- Why `floor(log1p(multiple))` instead of manual 0.5‑width bins on `log1p(multiple)`?

  - What you are considering:
    - Compute `z = log1p(multiple)`.
    - Bucket `z` into bins of width 0.5 (e.g. [0,0.5), [0.5,1.0), … up to ~8.0).
    - Assign an integer grade per bin (0, 1, 2, …).
  - In practice, `floor(log1p(multiple))` is already a simple, robust binning scheme:
    - It partitions the log scale into unit‑width bins: [0,1), [1,2), …, which is coarse but aligned with your 0–8 range.
    - It is monotonic in `multiple` and produces a small number of integer grades, which is exactly what NDCG expects.
  - Using 0.5‑width bins adds complexity without clear benefit here:
    - You roughly **double** the number of label levels (more bins) but NDCG mainly cares about label **ordering**, not the precise spacing between grade values.
    - More bins means fewer examples per grade level, which can introduce label sparsity and noise.
    - You would be re‑implementing a custom binning function that is harder to reason about than the already‑tested `calculate_relevance_grade`.
  - Recommendation:
    - Stick with `calculate_relevance_grade` as implemented (`floor(log1p(...))` with 0 for missing/≤0).
    - If you ever want coarser labels, it is simpler to **cap** the maximum grade (e.g. `min(floor(log1p(m)), 5)`) than to introduce new manual binning.

- How this plays with XGBoost LambdaMART:
  - Objective: `rank:ndcg` uses the label as a relevance degree; order matters more than exact spacing.
  - With labels 0–7 from `floor(log1p(max(unified_outcome)))`:
    - Founders with no exits or low outcomes (≤0×) get grade 0 (baseline).
    - Moderate exits (a few ×) land in the mid‑range grades.
    - Fund‑returning or extreme wins cluster into the top grades (6–7), which encourages the model to rank them above the rest.
  - Because the labels are bounded and log‑scaled, the model sees a reasonable gradient signal across most of the range, not just at the extremes.

ELI5:

- Think of `multiple` as a “founder score” in raw dollars:
  - Some founders have 0× (no return), some 2×, a rare few 100× or more.
- If you feed those raw numbers into the ranking model:
  - The difference between 100× and 200× would dominate training, even though both are already huge wins.
  - The model spends a lot of effort explaining tiny differences among the already‑amazing founders.
- Instead, you:
  - Take the **log** of the multiple (after adding 1 so 0 is safe): big numbers get squeezed; 2× vs 3× is still visible, but 100× vs 200× becomes a much smaller gap.
  - Round that log value down to an integer **grade** (0–7).
  - Use that grade as the “relevance level” for each founder:
    - 0 means “no meaningful win yet.”
    - 1–3 means “some success.”
    - 4–5 means “strong wins.”
    - 6–7 means “fund‑returner / extreme outlier.”
- The ranking model then learns: “founders with grade 7 should be ranked above grade 5, above grade 3, etc.” without getting confused by the raw size of the biggest exits.

Rationale:

- Business alignment:
  - The core KPI VCs care about in this exercise is **exit multiple** on capital; using `multiple` exclusively for labels makes the target directly reflect that objective.
  - `performance` is a related but different KPI, especially for non‑exited companies. Mixing it into labels when you already have `multiple` for every training founder would blur the definition of “success” and make labels harder to interpret.
- Data properties:
  - Because every training founder has at least one founded company with a recorded `multiple`, there is **no label coverage gap** that needs to be patched with `performance`.
  - Using only `multiple` avoids injecting extra noise from `performance` (which is on a different scale and definition) and keeps labels consistent across all founders.
- Statistical behavior:
  - Raw `multiple` is extremely heavy‑tailed; `log1p` compresses that tail and stabilizes the signal without losing the ordering of outcomes.
  - Converting `log1p(multiple)` to an integer via `floor` provides a small, dense set of relevance levels. This is enough for NDCG, which mainly needs a **ranking of labels**, not finely calibrated distances between them.
  - Adding extra 0.5‑width bins would create more label levels, but would thin out the data per level and add noise without giving the ranking objective a clear benefit.
- Simplicity and maintainability:
  - The label path “max multiple → `calculate_relevance_grade` → `relevance_grade`” is short, easy to explain, and matches the production code (`src/models/metrics.py`).
  - Avoiding custom binning logic (0.5‑width bins) and avoiding label‑side use of `performance` keeps the training pipeline aligned with the SIMPLE principle: fewer moving parts, less chance of train/serve drift or conceptual confusion later.

Conclusion:

- For LambdaMART with XGBoost **on your current training founders**, the recommended handling of `multiple` is:
  1. Ignore `performance` for label construction because every training founder has at least one founded company with a `multiple`; `performance` stays a feature only.
  2. For each founder, compute a scalar outcome from multiples alone, e.g. `founder_outcome = max(multiple)` over all companies they founded.
  3. Map that scalar via `calculate_relevance_grade`, which effectively does `label = floor(log1p(founder_outcome))` and returns an integer grade in `{0,…,7}` with 0 for missing/≤0.
  4. Use this `relevance_grade` as the target label for LambdaMART (with NDCG) at the founder level, grouped by `(industry, founded_year)` or similar cohorts.
- This approach:
  - Respects the heavy‑tailed nature of multiples via a log transform.
  - Produces stable, interpretable integer relevance levels.
  - Aligns with your existing `calculate_relevance_grade` helper and design docs, minimizing custom binning logic scattered across notebooks.
  - Avoids unnecessary unification with `performance` and avoids extra 0.5‑width binning on `log1p(multiple)`, keeping the label transform simple and maintainable.
