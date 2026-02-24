# GV Founder Ranking Case Study

Turn the provided founder history data into a repeatable ML pipeline that (1) trains an XGBoost ranker on curated data and (2) scores the "interest list" of new founders with an accompanying explanation.

```
scripts/train.py --config configs/base.yaml
scripts/batch_predict.py --config configs/base.yaml
```

## Architecture

```
scripts/ (train.py, batch_predict.py)
  ↓
src/common/        # config, logging, error contracts
src/data/          # schema validation + typed datasets
src/features/      # feature builders returning FeatureMatrix
src/models/        # model bundle loader + training artifacts
src/predict/       # batch inference + SHAP explanations
configs/           # YAML configs pointing at src/data/{training,real}
```

Contracts are expressed as dataclasses:
- `RankingRawData`/`RankingCleanData` (data layer)
- `FeatureMatrix`/`FeatureMetadata` (feature layer)
- `ModelBundle` (model layer)
Each stage only accepts the upstream contract, so a reviewer knows exactly which code owns which responsibilities.

## Getting Started

1. **Python** – Use Python 3.10+ (`pyenv` or system Python).
2. **Create env + install**
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install --upgrade pip
   pip install -e .[dev]
   ```
3. **Configure paths** – `configs/base.yaml` already points to `~/Desktop/gehirn/gv_case_study/src/data`. If your repo lives elsewhere, edit `project.root` or supply `--config /path/to/custom.yaml`. The `data.ranking_files.*` entries control inference CSV names and `data.training_files.*` controls training CSV names so you don't have to touch code when filenames change.
4. **Train** – builds features from `src/data/training`, fits `XGBRanker`, and writes `experiments/models/{ranker.json,artifacts.json}`:
   ```bash
   python scripts/train.py --config configs/base.yaml --env dev
   ```
5. **Batch inference** – scores the "real" founders and writes `experiments/ranked_founders.csv` with SHAP-based explanations:
   ```bash
   python scripts/batch_predict.py --config configs/base.yaml --shap-top-n 3
   ```
6. **Tests + lint** – focuses on schema validation, feature building, and model IO:
   ```bash
   pytest
   ```

You can also use the `Makefile` shortcuts:

- `make install` – create `.venv` and install dependencies in editable mode.
- `make test` – run the test suite inside the virtualenv.

## Approach & Limitations

- **Model** – Gradient-boosted pairwise ranker (XGBoost) trained on founder-level features (prior roles, exits, education tier, years of experience). Targets are graded multiples (0–5) derived from the provided `multiple` column via `calculate_relevance`.
- **Features** – Derived purely from historical experience + education. No text or graph features yet; role velocity, team composition, and industry alignment remain TODO.
- **Data validation** – Pandera schemas on every CSV catch missing/renamed columns before they leak into notebooks. Schema drifts hard fail with `SchemaMismatchError`.
- **Configuration** – Single YAML file controls every path; placeholders (`${project.root}`) guarantee that CI, notebooks, and scripts use the same directories. `src/common/config.load_config` enforces typed contracts before any code executes.
- **Limitations** – Education tier is averaged rather than modeling the full distribution; SHAP explanations operate on the boosted trees and can be noisy for sparse rows; no automated hyperparameter search; streaming / online scoring not yet implemented (batch only).

## Follow-up Answers (from `ana_0.md`)

1. **Improvements & new insights** – Expand feature set with founder-team composition (number of co-founders, executive mix), tenure velocity (average time to next role), and education field diversity. Pair this with cohort-based calibration so the score reflects industry baselines.
2. **Measuring performance** – Use NDCG@K (mirrors investor workflow of reviewing top slices), supplemented with precision @20 on "excellent" founders (grade ≥4). Backtest on historical vintages held out by year to ensure generalization across cycles.
3. **New data sources** – Enrich with fundraising databases (Crunchbase, PitchBook), patent filings (for deep tech signals), GitHub / arXiv velocity for technical founders, LinkedIn/PeopleGraph for team relationships, and market data for current traction.
4. **Scaling to 100M founders** – Materialize features via Spark or Beam jobs writing to a feature store (Feast/Tecton) and convert training/inference to run on GPU-backed distributed XGBoost. Batch inference uses chunked Parquet partitions, feeding a vectorized predict service behind a queue.
5. **Production + real-time scoring** – Promote `ModelBundle` to a versioned registry (MLflow). Wrap inference logic (`run_inference`) in a FastAPI service that caches the latest bundle, accepts JSON payloads validated by Pydantic, and streams SHAP at request time. Use Kafka/Kinesis to capture founder updates and trigger incremental feature recomputations.
6. **Other roles / industries** – Parameterize feature builders with role-specific templates: for C-suite, emphasize leadership tenure and operational scope; for scientists, track publications, patents, and grant success. Add an `industry` dimension to config so feature lists and scoring weights become per-industry modules, enabling a multi-head model trained with shared infrastructure.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `SchemaMismatchError` when loading CSVs | Confirm the raw files kept required columns (`person_id`, `education_tier`, etc.). Re-run notebooks to regenerate or update `src/data/real`. |
| `Model or artifacts not found` | Run `scripts/train.py` or point `configs/base.yaml -> model.artifact_dir` at an existing run. |
| `ImportError: src.*` | Ensure you ran `pip install -e .` or invoke scripts via `python -m`. |
| Slow SHAP step | Use `--shap-top-n 0` on `scripts/batch_predict.py` to skip explanation generation. |

The generated ranked CSV lives at `experiments/ranked_founders.csv` by default and includes `founder_id,score,rank,explanation` as required.
