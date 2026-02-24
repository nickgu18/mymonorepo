success criteria of answers: comprehensive, and also include a ELI5 section for beginners.

Question:

For inference data, how many founders have `performance` tied to their last founded company? How about across all the companies they have founded? I also want to know this for both training and inference.

Analysis:

- Data sources:

  - Training: `founder_experience_training.csv` + `company_info_training.csv`.
  - Inference: `founder_experience.csv` + `company_info.csv`.
  - All were loaded via the existing `load_config` / `load_and_clean` helpers so IDs are normalized and `performance` is coerced to numeric, with missing values kept as `NaN`.

- Who counts as a founder:

  - Start from the cleaned `experience` tables.
  - Normalize `is_founder` to a boolean (`True` when the string is one of `{"true","1","yes","y","t"}`).
  - Keep only rows with non-null `person_id` and `company_id`.
  - A “founder” is any `person_id` with at least one such row.

- “Last founded company” per founder:

  - Each experience row has an `order` column giving the sequence of roles.
  - For each founder, sort their founder rows by `person_id, order` (descending), then take the first row.
  - Join that `company_id` to the appropriate `company_info` table and check whether `performance` is non-null.

- “All founded companies” coverage:

  - For each founder, collect the set of all `company_id` values where `is_founder == True`.
  - Build a lookup `company_id -> performance` from the relevant `company_info` table (after normalization).
  - For each founder:
    - “All founded companies have performance” if every founded `company_id` has a non-null `performance`.
    - “At least one founded company has performance” if any founded `company_id` has a non-null `performance`.
    - “No founded companies have performance” if none of their founded companies have performance.

- Results (using the above definitions):
  - Training founders:
    - Total founders: **4,772**.
    - Founders whose **last founded company** has performance: **3,610**.
    - Founders with performance for **all** founded companies: **3,168**.
    - Founders with performance for **at least one** founded company: **4,223**. (this is 4223/4772=88.6%)
    - Founders with **no** performance for any founded company: **549**.
  - Inference founders:
    - Total founders: **120**.
    - Founders whose **last founded company** has performance: **30**.
    - Founders with performance for **all** founded companies: **23**.
    - Founders with performance for **at least one** founded company: **48**. (this is 48/120=40%)
    - Founders with **no** performance for any founded company: **72**.

ELI5:

- Think of each founder as a student and each founded company as one of their courses.
- The `performance` column is like the final grade for that course.
- The questions we answered are:
  - “Does this student have a grade for their **most recent course**?” (last founded company).
  - “Does this student have grades for **all** the courses they’ve ever taken?” (all founded companies).
- In training, most founders have at least one graded company and many have grades for every founded company.
- In inference, most founders **don’t** have any graded companies, and only a small minority have grades for their last or all founded companies.

Conclusion:

- Training data:
  - About **76%** of founders (3,610 / 4,772) have `performance` available for their **last founded company**.
  - About **66%** of founders (3,168 / 4,772) have `performance` for **all** their founded companies.
  - Only **549** founders (≈11%) have **no** `performance` for any founded company.
- Inference data:
  - Only **30** of **120** founders (25%) have `performance` for their **last founded company**.
  - Only **23** founders (≈19%) have `performance` for **all** their founded companies.
  - A majority, **72** founders (60%), have **no** `performance` for any founded company in `company_info.csv`.
- Practically, this means `performance` is a reasonably well-covered signal in training but a sparse, partially missing signal in inference, so you should rely on models that can handle missing values natively (like XGBoost) and avoid assuming performance is present for most inference founders.
