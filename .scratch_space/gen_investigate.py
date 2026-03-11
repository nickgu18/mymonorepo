blob = """## Investigation Summary

**Root Cause:**
There are multiple interconnected issues causing heal runs to not show task breakdowns, fail to update the status to 'healing', and crash with `Task state is updated from RUNNING to FAILED`. 

1.  **Task Breakdown is empty:** When a job is healed, the `eval_results_jobs` table gets a new row inserted. However, the UI fetches the task instances via `GET /api/jobs/{job_id}/instances` which calls `bq_client.list_instances(job_id)`. The issue is that `job_id` here is the *original* BenchHub Run ID, and the instances table is correctly matching it. However, the UI's `RunBrowser` might be confused because the *new* job row doesn't have the instance counts yet until the worker finishes parsing. BUT, looking closer at the error log, the worker is actually **crashing** before it can parse the instances.
2.  **Worker Crash:** The error `Job failed due to task failure... exit code 1` means the `entrypoint.sh` script is failing. We recently refactored `entrypoint.sh` to extract the inline Python zip scripts into `worker/scripts/get_run_folder.py` and `worker/scripts/safe_extract.py`.
    However, the `RUN_FOLDER_NAME=$(python3 /app/scripts/get_run_folder.py)` command is likely failing because the script is reading `zip_path = "raw_logs.zip"` but the zip file might not exist yet if the GCS download failed, OR the python script is throwing an exception and returning nothing, causing `mkdir -p ""` which fails with `mkdir: cannot create directory ‘’: No such file or directory`. 
3.  **Status not updating:** The orchestrator sets the status to `RUNNING` in BigQuery right after submission. However, when the Cloud Batch job starts, the `sidecar_monitor.py` runs its `upsert_job` logic. Due to our recent change where `upsert_job` matches on both `run_id` and `job_id`, the sidecar inserts a brand new row. If the worker immediately crashes (due to the script error), the new row gets marked as `FAILED`, and the instances are never parsed.

**Impact:** Heal jobs immediately crash on startup, preventing any resume operations. The UI is left in an inconsistent state displaying the failed heal attempt with 0 instances parsed.

**Reproduction:** Trigger a heal on any broken job. The Cloud Batch worker fails immediately because `entrypoint.sh` hits an error running the extracted python scripts.

## Order

**Intent:** Fix the worker entrypoint crash by ensuring the extracted python scripts handle edge cases correctly and don't break the shell script.

**Constraints:**
- Must maintain the extracted python script structure.
- Must ensure `RUN_FOLDER_NAME` is never empty.

**Done-when:**
- [ ] `get_run_folder.py` safely falls back to a default folder name if the zip file is missing or corrupted.
- [ ] `entrypoint.sh` gracefully handles the extracted variables.
- [ ] Heal jobs successfully download, resume, and upload results.

**Resources:**
- `worker/scripts/get_run_folder.py`
- `worker/entrypoint.sh`

**Fix Plan:**
1.  **`worker/scripts/get_run_folder.py`:** Update the script to ensure it ALWAYS prints a fallback folder name (e.g., `eval-unknown`) even if reading the zip file completely fails. Currently, if an exception happens *before* `run_folder_name` is initialized, it might print an empty string or crash.
2.  **`worker/entrypoint.sh`:** Add a safeguard: `if [ -z "$RUN_FOLDER_NAME" ]; then RUN_FOLDER_NAME="eval-$RESUME_FROM_RUN_ID"; fi` to ensure `mkdir` never fails with an empty string. 
3.  **`worker/scripts/safe_extract.py`:** Ensure the script exists and has correct permissions. Wait, in `patch_dockerfile.py` we copied `worker/scripts` to `/app/scripts`. Let's verify the Python scripts are actually there and executable.
"""

with open("/usr/local/google/home/guyu/Desktop/mymonorepo/.scratch_space/tasks/investigate.md", "w") as f:
    f.write(blob)
