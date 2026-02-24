# Evaluation of XGBoost Founder-Ranking Submission

## 1. Overall Assessment

- The submission shows strong engineering skills: clean modular design (`data` → `features` → `models` → `predict`), typed config objects, and a small but well-targeted test suite that mirrors the notebook process.
- On the modeling side you demonstrate solid understanding of ranking problems (NDCG@K, recall@K, cohort-based time splits, leakage concerns, skewed labels, distribution shift).
- There are some important but fixable modeling and production-readiness gaps (mostly around labels, time-respecting features, and cross‑industry ranking), but nothing that suggests a lack of core expertise.
- Overall, this would count as a “yes, sufficiently strong” submission for someone expected to own this kind of pipeline, provided you can speak clearly to the limitations below and how you would address them.

## 2. Additional Shortcomings and Improvements

Below are limitations that are present in the code but not fully called out in your README.

### 2.1 Label definition and use of multiple outcomes

- Root cause: The current training pipeline is part-way through a transition from “last labeled company” semantics to “max multiple” semantics. The helper is now named `_build_max_multiple_labeled_company_metadata`, which matches your written goal (use the best outcome a founder has achieved), but its docstring and surrounding comments still talk about “last” company behaviour and there is no dedicated test asserting the max‑multiple contract.
- Impact:
  - It’s easy for future changes to accidentally reintroduce “last company” behaviour or some hybrid, because the intended label definition is not encoded in tests or clearly documented in one place.
  - Reviewers have to reverse‑engineer from notebooks and code comments what the label actually is, which makes the model harder to reason about and to compare against baselines.
- Improvements:
  - Make the contract explicit: pre‑aggregate `target_variable_training` to a founder-level label table (e.g. `label_max_moic`, optionally `label_last_moic` alongside it) and implement `_build_max_multiple_labeled_company_metadata` as a thin join against that table.
  - Add a small, direct unit test that constructs a toy founder with two labeled companies and verifies that the helper picks the max‑multiple company, so the intended behaviour cannot silently drift.

### 2.3 Cross-industry ranking vs group-based objective

- Root cause: In `split_by_industry` you use industries as XGBoost “groups” (ranking is enforced within each industry), but in `predict_batch` you create a **global** rank by sorting on the raw score across all industries.
- Impact:
  - `XGBRanker` only optimizes relative ordering within each group; absolute score scales across groups are not guaranteed to be comparable.
  - A founder in an industry with more extreme score ranges can end up globally outranking equally strong founders from a “flatter” industry, even if per-industry ordering is correct.
- Improvements:
  - Either (a) treat **each ranking scenario** (e.g. “this week’s candidate list”) as a single group and include `industry` as a feature, or (b) keep industries as groups but output **per-industry leaderboards** (ranking within each group) instead of a single global ranking.
  - If you need a global list, consider a calibration step per industry (e.g. map scores to within-industry percentiles, then rank on calibrated scores).

### 2.5 Evaluation nuances for near-all-zero cohorts [added]

- Root cause: Some industry-by-year cohorts have almost all labels at the lowest grade (due to very recent founding years). Your tests and metrics correctly compute NDCG/recall, but you treat all cohorts the same.
- Impact:
  - NDCG and recall are effectively undefined or uninformative when **all** labels in a group are zero; those groups get a flat score of 0.0 even if the model is behaving as well as possible under the data.
  - Mean metrics across industries can be dragged down by these cohorts and make the model look worse than it is on more mature segments.
- Improvements:
  - Report metrics separately for “mature” vs “young” cohorts, or weight groups by the number of positive labels when averaging.
  - Explicitly call out in the README that performance on very recent vintages is structurally constrained by the lack of realized outcomes.

### 2.6 Operational/packaging issues

- Root cause: `configs/base.yaml` in the submission points `project.root` to an absolute path (`~/Desktop/gehirn/gv_case_study/xgboost`) and tests expect pre-existing MLflow `notebook_runs` artifacts on disk.


## 3. Draft Answers to Follow-Up Questions

Below are concise answers you could give to the follow-ups from `ana_0.md`, written to align with your current implementation and the critique above.

### 3.1 If you were to expand on your solution, in what ways might it be improved?

- First, I would tighten the **label definition**: aggregate the target table to founder-level `max_moic` (and possibly `last_moic`) and train explicitly on that, removing the ambiguity between “last labeled company” and “best outcome”.
- Second, I would fully wire in the richer **founder features** I prototyped: experience counts and tenure, founder-level performance aggregates, first-degree network size/quality, and founding team size, all computed in a time-respecting way up to the founding year.
- Third, I would revisit the **cohorting strategy**: keep intra-industry ranking, but either produce per-industry leaderboards or explicitly calibrate scores across industries so that a global “Top N founders” list is meaningful.
- Finally, I’d add systematic **hyperparameter search** (e.g. Optuna/MLflow integration) over `n_estimators`, depth, learning rate, and regularization using a year-based validation split, and use those runs to benchmark against a simpler baseline (e.g. purely heuristic score).

### 3.2 What other insights can you glean from the data that you have extracted?

- From the performance table, we can see that **realized outcomes are extremely skewed**: most companies are low multiple or zero, with a very long tail of outliers. That justifies the log transform and grade-based labels instead of trying to regress raw multiples.
- The experience and education tables suggest that there are distinct **founder archetypes**: repeat founders with concentrated startup experience, corporate executives transitioning into founding roles, and deep-technical founders with fewer roles but higher education tiers. Each archetype appears to have different outcome distributions.
- Using the network features, we could analyze whether **network size and quality** (as proxied by co-worker education tiers) correlate with better outcomes after controlling for industry and founding year, which would inform whether we want to operationalize those signals in scoring.

### 3.3 How would you measure the performance of your solution?

- The primary metric would be **NDCG@K per cohort** (industry × vintage), because that directly measures whether the highest-outcome founders are ranked near the top of the list the investors actually review.
- I would complement that with **recall@K** on high-grade founders (e.g. grade ≥ 3 or ≥ 4 after the log/grade transform) to answer the business question “if we contact the top N, what fraction of the truly exceptional founders did we capture?”.
- Evaluation should be **time-based**: hold out the most recent years as test, and optionally a middle slice as validation for tuning. Reporting metrics separately for older and more recent cohorts helps us see both how the model generalizes across cycles and how much performance is structurally limited by unobserved outcomes.

### 3.4 What other data sources would you want to integrate to improve your scoring?

- **Company performance and traction**: fundraising histories, revenue/ARR, user growth, and retention from sources like Crunchbase or internal portfolio systems would let us distinguish “great founder in a bad market” from “average founder in a booming market”.
- **Network and reputation**: richer professional graph data (LinkedIn-like signals, mutual investors, board memberships) would give us more robust measures of founder centrality and access to capital/talent than co-worker overlaps alone.
- **Technical and scientific signals** for deep-tech: publications, patents, open-source activity, and grant success rates would be particularly relevant for scientific founders.
- All of these would feed into additional, mostly numeric features; the XGBoost ranker can absorb them without changing the core architecture.

### 3.5 Imagine you now have 100 million founders to rank. How would you scale up your solution?

- I would separate the system into:
  - an offline **feature generation pipeline** (Spark/Beam jobs reading raw tables and writing features to a feature store or partitioned Parquet), and
  - a **distributed training** stage using XGBoost on GPUs (or on a cluster via Dask/Ray) with chunked training data.
- For scoring 100M founders, I would:
  - run **batch inference** over partitions (e.g. by geography or industry) writing scores to an analytical store, and
  - maintain pre-computed **top-K indexes** per segment so that user-facing applications can query “top founders in X” without scanning all 100M rows.
- The current contract-based design (clean data → feature matrix → model bundle) already lends itself to this: we mostly need to swap out in-memory Pandas with distributed equivalents and make IO explicit and streaming-friendly.

### 3.6 How would you productionize it and support real-time scoring for new founders?

- I would keep the model bundle (`ModelBundle`) as the deployable unit and:
  - register versions in a model registry (e.g. MLflow) along with their feature schema and evaluation metrics, and
  - deploy a small **scoring service** (FastAPI/Go) that loads the latest approved bundle and exposes a `/score_founder` endpoint.
- Real-time scoring would work by:
  - looking up or computing the required features for a new founder from a **feature store** (or a fast cache keyed by `person_id` / `company_id`),
  - running the XGBoost model to get a score and a short, SHAP-derived explanation, and
  - optionally emitting the request/response to a stream (Kafka/PubSub) for monitoring and later re-training.
- Batch and online paths would share the same feature definitions and bundle format, so that behavior is consistent between offline evaluation and real-time decisions.

### 3.7 How would you modify your solution for other roles or to rank within specific industries?

- For other roles (C‑suite, lead scientist, marketing), I would:
  - keep the same overall architecture but **change the label definition** (e.g. success in that role type, promotion velocity, retention), and
  - adjust feature builders to focus on role-relevant signals: leadership tenure and org scope for executives, publications/patents for scientists, campaign or growth metrics for marketing leaders.
- For industry-specific ranking, I would:
  - either train **separate models per broad industry** (tech, consumer, life sciences) or introduce an industry-specific head on top of shared features, and
  - ensure evaluation and calibration are reported per industry so investors can compare “top 50 AI founders” vs “top 50 consumer founders” on their own terms.
- The core data contracts (clean tables, feature matrix, model bundle) would stay the same; what changes is the labeling logic and the feature configuration per role/industry.
