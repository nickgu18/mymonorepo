### task
Ensure that BigQuery properly overwrites or upserts the task status rather than appending duplicate rows for the same task attempt during a 'heal' operation. Fix inflated metrics in the `eval_jobs` table caused by repeated terminal status reports for the same task.

### constraints
- If a task fails again during a heal, the state needs to be managed carefully to avoid duplicate token counting or inflated metrics.
- BigQuery schema and query logic must support deduplication based on `run_id`, `dataset_id`, and `instance_id`.
- Maintain accurate total token counts without double-counting initial failures (if overwriting is the desired behavior for tokens).

### definition of done
- A healed task's success or subsequent failure correctly overwrites its previous state in the `eval_results_instances` table.
- `completed_instances`, `passed_instances`, `failed_instances`, and `error_instances` in `eval_results_jobs` are accurately reflected even after multiple "heals".
- Token counts in `eval_results_jobs` do not double-count if a task is retried (assuming latest attempt should win, or as specified by user).
- `total_instances` in `eval_results_jobs` does not shrink during heal operations.
- Integration tests confirm data consistency in BigQuery after a heal.

### fix_plan
1.  **Modify `BigQueryClient.upsert_job`** in `projects/bench-hub/common/src/bench_hub_common/bigquery.py`:
    -   Update the `MERGE` logic for `total_instances` to only update if the new value is greater than the existing value.
2.  **Implement `BigQueryClient.update_job_progress_on_transition`**:
    -   This new method will handle the logic of transitioning an instance from one status to another.
    -   If an instance was previously `ERROR` and is now `PASSED`, it should:
        -   Decrement `error_instances`.
        -   Increment `passed_instances`.
        -   Keep `completed_instances` same.
    -   If an instance was previously `RUNNING` or `None` and is now terminal:
        -   Increment `completed_instances`.
        -   Increment the respective status count.
3.  **Modify `BigQueryClient.upsert_instance`**:
    -   Fetch the existing instance status before the `MERGE`.
    -   Perform the `MERGE`.
    -   Call `update_job_progress_on_transition` instead of `increment_job_progress`.
    -   Decide on token strategy: If "no double counting" is required, the `MERGE` should overwrite tokens, and the job update should adjust the delta.
4.  **Update `sidecar_monitor.py`** if necessary to ensure it doesn't suppress heal reports (it already seems to allow re-reporting).
5.  **Add/Update tests**:
    -   Verify the transition logic in `test_bigquery_client.py`.
    -   Verify `total_instances` protection.

### files
- projects/bench-hub/common/src/bench_hub_common/bigquery.py
- projects/bench-hub/worker/sidecar_monitor.py
- projects/bench-hub/worker/tests/test_bigquery_client.py
