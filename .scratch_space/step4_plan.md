### task
Add a loop or completion logic to detect when a heal job finishes, triggering a re-evaluation of the parent run so its broken status is cleared if fully resolved.

### constraints
Needs to tie a heal job's completion back to the parent job to re-evaluate the parent job's overall success securely and reliably.

### definition of done
- A mechanism (e.g., cron, Pub/Sub, or orchestrator background loop) detects a heal job completion.
- When the heal job completes, the system queries all tasks for the *parent* job.
- If all tasks for the parent job are now successful, the parent job's status transitions to `COMPLETED`. If some still failed, it goes back to `BROKEN`.

### fix_plan
1. Identify how regular jobs are marked `COMPLETED` (e.g. `_sync_jobs_with_batch` or Pub/Sub trigger).
2. For heal jobs, identify their parent `job_id` (via `heal_of` tag or by querying the `job_id` they reference).
3. Upon a heal job completing, instead of just updating the heal job's status, trigger a re-evaluation of the parent `job_id`.
4. The re-evaluation logic aggregates the latest statuses of all tasks for the parent `job_id`.
5. Update the parent `job_id` to `COMPLETED` or `BROKEN` depending on the aggregation result.

### files
- `projects/bench-hub/orchestrator/main.py`