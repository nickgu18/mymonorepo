# LLM-Driven Founder Ranking PRD

## 1. Overview
This document outlines the design and implementation plan for an LLM-based system to rank startup founders. The goal is to leverage the semantic understanding of Large Language Models to identify high-potential founders, capturing qualitative signals (trajectory, quality of experience) that traditional XGBoost models might miss.

## 2. Success Criteria
- **Implementation**: A working pipeline that ingests raw CSV data and outputs a ranked list of founders with explanations.
- **Performance**: The ranking should correlate with "success" (ROI multiples) better than random chance, validated via backtesting.
- **Explainability**: Every ranking decision (or at least the final score) must be accompanied by a natural language explanation of *why* a founder is promising.

## 3. Architecture

The system follows a **Pairwise Ranking Prompting (PRP)** architecture, treating the LLM as a comparator function `cmp(A, B)` within a standard sorting algorithm.

### 3.1 High-Level Flow
1.  **Data Ingestion**: Load training CSVs (`founder_experience`, `education`, `company_info`, `target_variable`) that contain the labeled founder scores.

2.  **Feature Engineering**:
    -   **Hard Features**: Compute static metrics (e.g., Network Quality, Experience Duration).
    -   **Profile Serialization**: Convert each founder's history into a structured Markdown representation.
3.  **Ranking Engine**:
    -   Use a sorting algorithm (Merge Sort) driven by an LLM Comparator.
    -   **Comparator**: An LLM Agent that takes two profiles and decides which is "better" based on investment criteria.
4.  **Output Generation**: Produce a ranked CSV for the held-out test split of the training data with `person_id`, `rank`, `founder_score` (derived from rank), and `explanation`.
5. **Prediction**: Run the trained comparator on the real/inference dataset to predict founder scores with explanations for each person_id. This workflow is packaged in `llm_driven_ranking/notebooks/founder_score_inference.ipynb` so the team can review and re-run inference interactively.

## 4. Data Pipeline & Feature Engineering

### 4.1 Input Data
-   **Training**: `llm_driven_ranking/data/training/`
-   **Inference**: `llm_driven_ranking/data/real/`

### 4.2 "Hard" Feature Extraction
Before passing data to the LLM, we compute dense features to augment the text profile.

1.  **Network graph (not a feature)**:
    -   *Definition*: An undirected graph where nodes are people and edges are co-worker relationships.
2.  **Network Size Direct (direct_network_size)**:
    -   *Definition*: Number of first-degree connections.
    -   *Implementation*:
        -   Build a mapping: `Company -> List[Person]`.
        -   For each `Person`, find all `Co-workers` (people who worked at the same `company_id` during overlapping `start_date`/`end_date`).
        -   Count unique `Person` IDs.
3.  **Network Size Indirect (indirect_network_size)**:
    -   *Definition*: Number of all reachable nodes in the network graph.
    -   *Implementation*:
        -   Build a mapping: `Company -> List[Person]`.
        -   For each `Person`, find all `Co-workers` (people who worked at the same `company_id` during overlapping `start_date`/`end_date`).
        -   Count unique `Person` IDs.  
4.  **Network Quality (network_quality)**:
    -   *Definition*: Average Education Tier of first-degree connections.
    -   *Implementation*:
        -   Build a mapping: `Company -> List[Person]`.
        -   For each `Person`, find all `Co-workers` (people who worked at the same `company_id` during overlapping `start_date`/`end_date`).
        -   Look up `Education Tier` for all co-workers.
        -   Compute average.
5.  **Average Role Duration (avg_role_duration)**:
    -   *Definition*: Mean duration per role.
    -   *Implementation*:
        -   Build a mapping: `Person -> List[Role]`.
        -   For each `Role`, compute duration.
        -   Compute average.

### 4.3 Profile Serialization (Markdown)
The LLM performs best with Markdown tables. Each founder profile should be serialized as follows:

```markdown
## Founder: {person_id}

### Education
| Degree | Institution | Tier |
|--------|-------------|------|
| BS CS  | Stanford    | 5    |

### Experience
| Company | Role | Start | End | Duration | Job Type |
|---------|------|-------|-----|----------|----------|
| Google  | SWE  | 2010  | 2012| 2 yrs    | Employee |
| Stripe  | PM   | 2012  | 2015| 3 yrs    | Employee |

### Derived Metrics
network_size_direct
network_size_indirect
network_quality
avg_role_duration
```

## 5. The Comparator Agent (LLM)

### 5.1 Prompt Strategy
We will use **Chain-of-Thought (CoT)** to ensure reasoning precedes the decision.

**Comparator Prompt**:
```text
System: You are an expert Venture Capitalist with a specialization in Seed Stage B2B SaaS.
User: I will present two founder profiles (A and B) as Markdown tables. Select the founder that is more likely to deliver the higher investor return (multiples or strong performance).

Focus on the following signals:
1. Trajectory & scope of responsibility growth.
2. Quality of prior companies/roles and founder-market fit.
3. Evidence of grit (tenure, repeat founder) and network leverage.

Profile A:
{{profile_a_markdown}}

Profile B:
{{profile_b_markdown}}

Reasoning: Briefly compare A vs B referencing the signals above.
Decision: Return ONLY `A` or `B` (no prose) for the winner.
```

### 5.2 Handling Hallucinations & Bias
-   **Permutation Check**: Run `cmp(A, B)` and `cmp(B, A)`. If results conflict, treat as a tie or retry.
-   **Popular Vote**: Run five parallel comparator calls and pick the founder with the most votes to smooth out stochastic responses.
-   **Temperature**: Set to `0.0` for determinism.

## 6. Ranking Algorithm

Since comparing all pairs ($N^2$) is too expensive, we use **Merge Sort** ($N \log N$).

-   **Mechanism**: Implement a standard merge sort where the comparison `if left[i] < right[j]` is replaced by `if llm_compare(left[i], right[j]) == right[j]`.
-   **Optimization**:
    -   **Caching**: Store results of `(id_A, id_B)` comparisons in a local JSON/SQLite cache to avoid re-running identical queries during development/backtesting.
    -   **Batching**: If possible, batch requests to the LLM API (though Merge Sort is inherently sequential in its comparison steps, independent merges can be parallelized).

## 7. Implementation Plan

### Phase 1: Setup & Data Prep
1.  **`src/data_loader.py`**: Load CSVs and merge into a `Founder` object structure.
2.  **`src/feature_engine.py`**: Implement `calculate_network_quality()` and `serialize_profile_to_markdown()`.

### Phase 2: The LLM Engine
3.  **`src/llm_client.py`**: Wrapper around the LLM API (e.g., Gemini/OpenAI) with caching.
4.  **`src/comparator.py`**: Implement `compare_founders(f1, f2)` using the prompt template.

### Phase 3: Ranking & Execution
5.  **`src/ranker.py`**: Implement `merge_sort_founders(founders_list)`.
6.  **`main.py`**:
    -   Load Data.
    -   Run Ranker.
    -   Output `submission.csv`.

### Phase 4: Evaluation

7.  **Backtesting**:
    -   Predict the `founder_score` label (primary KPI). When we cannot observe that label directly (e.g., future inference cohorts), use company ROI multiples or downstream performance as the proxy target for monitoring drift.
    -   Build the split using `(year, industry)` groups so distribution stays consistent (e.g., earlier years per industry for train, later years per industry for test) and reuse the same grouping logic for the final holdout.
    -   Run ranking on the grouped test split and compute **NDCG** / **Precision@K** against the actual founder_score (and optionally ROI multiples).

#### Evaluation Question & Answer

-   **Question**: Given only `llm_driven_ranking/data/training/target_variable_training.csv` (exit multiples), `llm_driven_ranking/data/training/company_info_training.csv` (performance stats for non-exited companies), and `llm_driven_ranking/data/training/founder_experience_training.csv` (which founders built which companies), how do we build the ground-truth founder ranking used as the NDCG target when the true `founder_score` is defined as “ability to generate investor multiples/performance”?
-   **Answer**: Join `founder_experience_training.csv` → `company_id` so every founder is linked to each company they helped create. For each company, pull a single scalar `company_outcome`: use its realized multiple from `target_variable_training.csv` when present, otherwise derive a comparable performance score from `company_info_training.csv` (e.g., normalized TSR/growth percentile). Normalize both sources onto the same scale (0–1 or log-multiple) so exited and non-exited paths are comparable. Aggregate each founder’s outcomes (mean or tenure-weighted) to compute `founder_score_ground_truth`, then sort founders by that value to obtain the evaluation ranking. This derived rank is what NDCG/Precision@K compares against, ensuring we judge founders by the multiples/performance they actually produced.

## 8. Code Snippets (Copy-Paste Ready)

### 8.1 Profile Serialization
```python
def serialize_founder(founder, education, experience, metrics):
    md = f"## Founder: {founder.id}\n\n"
    
    md += "### Education\n"
    md += "| Degree | Institution | Tier |\n|---|---|---|\n"
    for edu in education:
        md += f"| {edu.degree} | {edu.institution} | {edu.tier} |\n"
        
    md += "\n### Experience\n"
    md += "| Company | Title | Start | End | Type |\n|---|---|---|---|---|\n"
    for exp in experience:
        md += f"| {exp.company_name} | {exp.title} | {exp.start_date} | {exp.end_date} | {exp.job_type} |\n"
        
    md += "\n### Metrics\n"
    md += f"- Network Quality: {metrics['network_quality']:.2f}\n"
    
    return md
```

### 8.2 Comparator Logic
```python
def compare_founders(profile_a, profile_b):
    prompt = f"""
    System: You are an expert Venture Capitalist with a specialization in Seed Stage B2B SaaS.
    User: I will present two founder profiles (A and B) as Markdown tables. Select the founder that is more likely to deliver the higher investor return (multiples or strong performance).

    Focus on:
    1. Trajectory & responsibility growth
    2. Quality of companies/roles + founder-market fit
    3. Grit + network leverage

    Profile A:
    {profile_a}

    Profile B:
    {profile_b}

    Reasoning: Briefly compare A vs B referencing the signals above.
    Decision: Return ONLY `A` or `B`.
    """
    response = call_llm(prompt)
    # Parse response to get winner ID
    return winner_id
```
