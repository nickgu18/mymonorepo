# Bench-Hub "Heal" Feature Analysis

This document provides a breakdown of how the "Heal" feature works and the known kinks based on the recent PR #57, and contextualizes it with the original Buganizer issue b/484405237.

## Bug Context (b/484405237)

**Title:** Need an easy way to "fix" a BenchHub run
**Status:** ACCEPTED / P0 (Assigned to guyu@google.com)

**Objective:** Implement a way to re-run only the tasks that failed due to infrastructure or transient issues (e.g., 4xx, 5xx errors, timeouts, `AgentSetupTimeoutError`, `AgentTimeoutError`, and `VerifierTimeoutError`) rather than re-running the entire job.
The goal is that upon fixing the run, the successful tasks from the original run are merged with the new results, emitting a new, updated Harbor run summary JSON file.

## How "Heal" Works (from PR #57)

The "Heal" feature is the prototype fulfilling the bug's objective. It retries only the failed tasks (`ERROR` or `CANCELED`) of a specific evaluation run while maintaining the original context.

### Architecture & Flow

```text
 ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
 │   Web UI    │       │     CLI     │       │   BigQuery  │
 │  (Run Summ) │       │  (heal cmd) │       │             │
 └──────┬──────┘       └──────┬──────┘       └──────┬──────┘
        │                     │                     │
        │    [POST /api/jobs/{job_id}/heal]         │
        └───────────────┐  ┌────────────────────────┘
                        ▼  ▼ (1) Identifies failed tasks
                 ┌──────────────────┐
                 │                  │
                 │   Backend API    │ (Proxy)
                 │                  │
                 └────────┬─────────┘
                          │ (2) Forwards request
                          ▼
                 ┌──────────────────┐ (3) Orchestrator queries BigQuery
                 │                  │     for ERROR/CANCELED tasks
                 │   Orchestrator   │     for this specific job_id
                 │                  │
                 └────────┬─────────┘
                          │ (4) Submits new Cloud Batch Job
                          │     - Passes specific '-t' task args
                          │     - Forces original BATCH_JOB_ID
                          ▼
                 ┌──────────────────┐
                 │   Cloud Batch    │
                 │     (Worker)     │
                 └──────────────────┘
```

1. **Trigger:** A user invokes the heal operation either by clicking "Heal" in the Web UI dashboard or running the `heal <job_id>` CLI command.
2. **Proxy:** The Backend receives the request and forwards it to the Orchestrator.
3. **Query Failed Tasks:** The Orchestrator (via the common BigQuery models) queries BigQuery to identify exactly which task instances failed (e.g., tasks that threw an `ERROR` or were `CANCELED`).
4. **Re-Execution:** The Orchestrator constructs a new Google Cloud Batch job submission. Crucially, it:
    * Modifies the entrypoint to pass only the specific failed tasks as arguments (`-t task1 -t task2`).
    * Overrides the `BATCH_JOB_ID` environment variable to ensure the telemetry and results from the "heal" workers map back to the original `job_id`.
5. **Update:** The worker sidecar monitors the execution. Upon success, the updated status overwrites the previous failure in BigQuery, moving the overall job status toward `COMPLETED`.

## Known Kinks (WIP)

Based on the commit notes ("still working out some kinks") and the architectural plan, the following areas represent the rough edges of the current prototype:

1. **State Management & Concurrency:** There is likely missing logic to prevent a user from triggering a "Heal" while the original job (or a previous heal) is still actively running.
2. **BigQuery Record Duplication/Overwriting:** Ensuring that BigQuery properly overwrites or upserts the task status rather than appending duplicate rows for the same task attempt. If a task fails again during a heal, the state needs to be managed carefully to avoid duplicate token counting.
3. **Cloud Batch Context Forcing:** Overriding the `BATCH_JOB_ID` inside the worker entrypoint is a bit of a hack (`fix(orchestrator): Override entrypoint to force BATCH_JOB_ID for heals`). Getting the metrics (like sidecar token extraction) to perfectly align with a hijacked job ID under the hood might still be causing downstream parsing issues.
4. **Result Merging (from the Bug definition):** The original bug explicitly calls out generating a *merged Harbor run summary JSON file*. The current flow updates BigQuery and the Web UI, but robust file merging on Google Cloud Storage might still be missing or unpolished.
5. **End-to-End Edge Cases:** What happens if the orchestrator fails to submit the Cloud Batch job after marking the job as "healing"? The UI might get stuck waiting for a job that was never queued.

*Status: The backend scaffolding is complete, but the robustness of the Cloud Batch retry mechanism is still heavily a Work-In-Progress.*