# Founder Prioritization PRD

## Problem Description
### Data overview
| Dataset | Key stats |
| --- | --- |
| `founder_experience_training.csv` | 54,616 rows covering 4,772 founders and 15,128 unique companies; median 9.5 experiences per founder (max 168). Job types skew toward `founder` (12.5k rows) and `employee` (12.1k), with 10k missing `job_type`. Binary flags show 25.7% of rows are founder roles, 22.7% c-suite, 14.4% board. |
| `education_training.csv` | Exactly one record per founder. Education tiers range 1–5 (mean 2.63) with highest levels: masters 36%, bachelors 32%, PhD 23%, associates 5%, high school 4%. |
| `company_info_training.csv` | 13,898 companies (IT 49%, Other 30%, Healthcare 21%). `performance` is 0–10, mean 2.63 with 46% missing. |
| `target_variable_training.csv` | 2,000 founder-led companies with ROI multiples (median 0, 75th percentile 3.25, max 2,957). Company founding years span 1980–2024 (median 2010); 61% are IT. |
| `founder_experience.csv` (ranking) | 1,583 rows for 120 new founders (mean 13.2 experiences each). Job mix similar but with slightly higher founder share (30%). |
| `education.csv` (ranking) | 120 founders with higher average tier (3.89) suggesting more elite schools than the training set. |
| `company_info.csv` (ranking) | 456 companies, `performance` observed for 34% (mean 2.65). Industries split: 48% IT, 42% Other, 10% Healthcare. |

### Observations & implications
- **Heavy-tail outcomes**: The ROI multiple distribution is extremely skewed (top 1% >100x). Modeling should focus on ranking rather than regression accuracy, and log-scaling multiples avoids exploding gradients.
- **Temporal drift**: Founding years cluster after 2001 with acceleration past 2010. The temporal split in the evaluation framework mitigates leakage and captures ecosystem shifts.
- **Missing company performance**: Almost half the company_info rows lack `performance`, especially in the ranking set (66%). Industry medians or similar proxies are necessary, and capturing uncertainty (e.g., penalty for unseen metrics) will stabilize the score.
- **Richer education in ranking data**: With 63% of ranking founders holding masters/PhDs vs 59% in training, we must avoid over-weighting education to prevent inflation of scores purely due to distribution shift.
- **Experience depth**: Founders average 11–13 recorded roles with high variance. Role order lets us compute velocity/tenure features, but noise (e.g., `false_position`, `intern`) suggests we need filters (minimum tenure, or down-weight job_type outliers).
- **Complete founder/target linkage**: Every company in `target_variable_training` appears in `founder_experience_training`, so we can confidently map realized multiples back to founder histories without external joins.

### Risks & mitigation
- **Data sparsity for young founders**: Recent founders have limited historical roles. Mitigation: rely more on company-level proxies (investor quality, co-founder network) and fall back to heuristic prior scores.
- **Explanation quality**: Rule-based text must remain faithful to quantitative contributions; we’ll log the numeric feature contributions used in every explanation to audit discrepancies.
- **Scalability**: Current datasets are <100k rows, but the approach must scale to millions. Using columnar storage plus vectorized feature computation keeps the footprint manageable, and the evaluation harness can sample when we stress-test.

This PRD plus `tools/summarize_data.py` sets the baseline understanding needed to implement the scoring system and generate the ranked founders list expected by the exercise.
