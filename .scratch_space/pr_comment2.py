import subprocess

comment = """Ah, great question! If everything uses the unified `BENCHHUB_RUN_ID` to manage state on disk and in GCS, you might wonder: **Why do we need a new `BATCH_JOB_ID` (job_id) at all?**

The new, distinct `job_id` exists strictly to satisfy **Google Cloud Batch infrastructure constraints** and to preserve **historical observability in BigQuery**.

Here is the exact role the new `job_id` plays in the PR:

### 1. Bypassing Cloud Batch Immutability
Google Cloud Batch (the GCP service that actually spins up the VMs) absolutely forbids reusing a Job ID. If we tell GCP "Hey, execute `job_123` again," it throws an error.
Therefore, the orchestrator generates a brand new ID for GCP (e.g., `job_123-heal-abcd`). This physical infrastructure ID is passed as `BATCH_JOB_ID`.

### 2. The 1:MANY History in BigQuery
While the worker container pretends it is `job_123` so Harbor works smoothly, the `sidecar_monitor.py` running alongside it captures the new `BATCH_JOB_ID` (`job_123-heal-abcd`) and uses it when syncing to BigQuery.

In `common/src/bench_hub_common/bigquery.py`, this new `job_id` is what triggers the `1:MANY` logic we built in the PR:
```sql
MERGE `eval_results_jobs` T
USING (...) S
ON T.run_id = S.run_id AND T.job_id = S.job_id
```

**Why is this important?**
If we just reused the original ID in BigQuery, the sidecar would ruthlessly overwrite the row of the original attempt. You would lose the data showing that the first attempt failed and only completed 40/80 tasks.

By using the new `BATCH_JOB_ID` in the `MERGE` statement:
* **Row 1:** `(run_id=job_123, job_id=job_123)` -> Shows the original failed attempt (e.g., 40/80 passed, Status: BROKEN)
* **Row 2:** `(run_id=job_123, job_id=job_123-heal-abcd)` -> Shows the new heal attempt (e.g., 80/80 passed, Status: COMPLETED)

### Summary
* `BENCHHUB_RUN_ID` handles the **Payload**: downloading the right zip, fooling Harbor into resuming, and overwriting the GCS artifacts.
* `BATCH_JOB_ID` handles the **Infrastructure & History**: keeping GCP happy and ensuring BigQuery tracks a discrete, append-only history of every single heal attempt."""

with open("comment2.txt", "w") as f:
    f.write(comment)

subprocess.run(["gh", "pr", "comment", "74", "-F", "comment2.txt"])
