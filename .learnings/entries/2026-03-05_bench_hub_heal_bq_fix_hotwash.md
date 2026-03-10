---
document_type: "Hot Wash Report"
exercise_name: "BenchHub BigQuery Heal Fix"
date: "2026-03-05"
evaluator_name: "Gemini CLI"
evaluated_organization: "BenchHub"
staff_section: "Engineering"
role_in_exercise: "Facilitator / Evaluator"
---

# HOT WASH REPORT FORM

## 1. Top Three (3) Organizational Strengths

1. **Surgical BigQuery Integration:** 
   - *Details:* Successfully implemented status transition awareness in `BigQueryClient.increment_job_progress` using delta updates to `eval_jobs` table, ensuring count and token accuracy.

2. **Proactive Total Instance Protection:** 
   - *Details:* Identified and fixed a bug where heal operations processing a subset of tasks would erroneously shrink the `total_instances` count in the job summary.

3. **Robust Automated Verification:** 
   - *Details:* Created a comprehensive transition-focused test suite (`test_bigquery_transitions.py`) and updated existing tests to verify the new three-query `upsert_instance` flow.

---

## 2. Top Three (3) Items Requiring Improvement

1. **Complexity of Atomic Updates:** 
   - *Details:* Current implementation relies on sequential queries (`SELECT` then `MERGE` then `UPDATE`) which, while functional for current loads, could benefit from more atomic BigQuery patterns if scale increases.

2. **Token Aggregation Policy Ambiguity:** 
   - *Details:* Had to infer if "no double-counting" meant overwriting tokens with the latest attempt or accumulating them; clearer product definitions on cost vs. attempt-performance would be beneficial.

3. **In-Memory State Synchronization:** 
   - *Details:* The reliance on `processed_instances` in the sidecar monitor works but is separate from the BigQuery state, potentially leading to inconsistencies if the monitor's local state is lost.

---

## 3. Hot Wash Remarks / Comments

- The orchestrator correctly sets `BENCHHUB_RUN_ID` for heal jobs, allowing for seamless record matching in the instances table.
- Use of `uv run pytest` proved efficient for running tests across different monorepo projects with complex `PYTHONPATH` requirements.
- The three-query flow in `upsert_instance` is a necessary trade-off for accuracy given BigQuery's limitations on multi-table `MERGE` or `RETURNING` clauses.
