### task
When the "Heal" button is clicked, immediately update those specific failed tasks back to QUEUED in BigQuery so the UI updates instantly.

### constraints
Needs to update the exact task records in BigQuery so the UI reads `QUEUED` or `PENDING` instead of `ERROR` for the healed tasks, ensuring that immediate frontend polls reflect this without waiting for new workers to spin up.

### definition of done
- `POST /api/jobs/{job_id}/heal` performs an explicit BigQuery update for failed tasks to set their status to `QUEUED` upon kicking off the heal job.
- Task status changes are immediately visible on the frontend without waiting for the new Cloud Batch workers to start.

### fix_plan
1. In `projects/bench-hub/orchestrator/main.py`, locate the `POST /api/jobs/{job_id}/heal` endpoint.
2. Add a synchronous BigQuery `UPDATE` call to update `status='QUEUED'` for `job_id={job_id}` and `task_id IN (...)` (the list of failed tasks determined for the heal operation).
3. Optionally, update the parent job's overall status to `HEALING` or `RUNNING` so the frontend knows a heal is in progress.

### files
- `projects/bench-hub/orchestrator/main.py`