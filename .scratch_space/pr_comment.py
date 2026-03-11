import subprocess

comment = """The fact that BenchHub intentionally forces Harbor's `eval_id` to equal `BENCHHUB_RUN_ID` is actually the core mechanic that makes this entire "Native Resume" PR possible!

Here is how that specific design choice directly powers the Heal implementation in this PR:

### 1. Deterministic GCS Downloading
When the orchestrator triggers a heal, it passes `RESUME_FROM_RUN_ID=job_123`. 
Because we know the `eval_id` matched the `run_id`, the worker immediately knows exactly where to look in GCS to find the previous state without needing a database lookup. It just executes:
`gsutil cp "gs://$GCS_BUCKET/job_123/raw_logs.zip" .`

### 2. Re-constructing the Harbor Workspace
This is the most critical part of the PR. For `harbor jobs resume` to work, the directory structure on the new worker must perfectly match what Harbor expects. Harbor expects to find a folder named after the `eval_id`.
Because the zip file `raw_logs.zip` was created *inside* the original run directory (not wrapping it), extracting it just dumps files into the current folder. 

In `worker/entrypoint.sh` (lines 177-194), we have a Python snippet that reconstructs the required directory. It peeks inside `raw_logs.zip`'s `config.json` to find the original `eval_id` (or `run_id`), creates a folder with that exact name, and extracts the zip *into* it. 

### 3. Native Harbor Execution
Once the folder structure `jobs/<eval_id>/` is reconstructed, the script runs:
`harbor jobs resume -p "$WORK_DIR/jobs/$RUN_FOLDER_NAME"`

Harbor looks at that folder, sees the `config.json` and the existing `result.json`, and seamlessly picks up where it left off. 

### 4. Overwriting State 
When the heal finishes, the trap function `save_artifacts` triggers. Because the `eval_id` and the `BENCHHUB_RUN_ID` are identical, it effortlessly zips up the newly merged directory and overwrites the exact same GCS path it downloaded from:
`cp "$WORK_DIR/raw_logs.zip" "$BUCKET_DIR/job_123/"`

**Conclusion:** 
If `eval_id` were a random UUID completely decoupled from the BenchHub `run_id`, we would have to implement complex tracking tables mapping `run_id -> [eval_uuid_1, eval_uuid_2]`, query them before downloading, and somehow tell Harbor to treat `eval_uuid_2` as a continuation of `eval_uuid_1`. 

Because they are identical, Harbor, BenchHub, and GCS all implicitly agree on the identity of the evaluation across multiple disjoint physical VM executions!"""

with open("comment.txt", "w") as f:
    f.write(comment)

subprocess.run(["gh", "pr", "comment", "74", "-F", "comment.txt"])
