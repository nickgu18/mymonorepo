# GehirnRepo = Monorepo for all projects

## Instructions

**ALWAYS FOLLOW YOUR GUIDING PRINCIPLES - `SIMPLE`**.

### Guiding Principles - SIMPLE

- S: Simplicity is preferred at all times.
  - Short docs
  - Short comments
  - Simple solutions
  - Simple but crucial logs.
- I: Investigate and research solutions before implement.
- M: Maintainability is not an after thought.
  - Code must be easy to read
  - Directory structure must be simple and clear
- P: Purpose Driven Development
  - Start with the purpose of the request
  - Develop corresponding test
  - Write and iterate on code until test passes without changing test code.
- E: Explain your decisions, always.
  - Explain the rootcause before suggesting solutions.
  - Explain the solution before implementation.

### Take Notes

During your interaction with the user, if you find anything reusable across projects (apps/services) (e.g. version of a library, model name), especially about a fix to a mistake you made or a correction you received, you should take note in the 'Codex learned' of the `Lessons` section in the `AGENTS.md` file so you will not make the same mistake again. 

### Consult Your Peers

1. When starting a project, ask project-manager for the project information.
2. If you are stuck, stop and ask for tech lead input (human).

### Stop and Check
**Stop and validate** at these moments:
- After implementing a complete feature
- Before starting a new major component  
- When something feels wrong
- Before declaring "done"

> Why: You can lose track of what's actually working. These checkpoints prevent cascading failures.

# Lessons

## Codex Learned

- When using XGBoost on tabular data, prefer its native handling of missing values (leave `NaN`s in the feature matrix) over custom median imputers that can hide missingness and leak target-aligned information.
- For highly skewed positive outcomes (e.g., venture multiples or revenue growth), a simple, reusable label transform is `log1p(max(value))` at the appropriate entity level (e.g., founder or customer) instead of coarse manual buckets.
- When a user explicitly asks for an explanation (e.g. “explain what function X is doing”), do not run code, modify files, or execute any “plan/execute” instructions; only inspect existing artifacts and describe behavior until the user clearly requests execution or code changes.
- In Jupyter notebooks `__file__` is not defined; use `Path.cwd()` (or a dedicated `_project_root()` helper) instead of `Path(__file__)` when constructing project-relative paths for notebook code.
- Keep feature builders (e.g. `build_matrix`) strictly label-agnostic: do not pass label-derived artifacts like `company_founded_lookup` from `target_variable_training.csv` into the feature pipeline; derive such context from non-label tables and handle label joins in a separate training dataset step.
- When collapsing per-founder experience into a single “last company” row, always ignore records with missing `company_id` first; otherwise, you silently drop founders whose final experience row lacks an ID.
- When building a labeled training frame, always ensure each training `company_id` actually appears in the target table and distinguish between missing labels due to pipeline joins vs. true gaps in the curated target data; only the latter should lead to dropped rows downstream.
- When adding time-respecting, post-split features (performance, network, team), extend shared helpers with optional per-entity cut-off mappings instead of changing existing call sites; this keeps tests passing while making the helpers reusable across notebooks and CLI flows.

- When using `XGBRanker` with group-based objectives (e.g. `rank:ndcg`), remember that the model only learns relative ordering *within* groups; raw scores are not guaranteed to be calibrated across groups, so global ranking should either be done per-group or via an additional calibration step.
