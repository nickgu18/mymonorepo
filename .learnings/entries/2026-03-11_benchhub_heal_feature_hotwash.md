---
document_type: "Hot Wash Report"
exercise_name: "BenchHub 'Heal' Feature End-to-End Implementation and Debugging"
date: "2026-03-11"
evaluator_name: "Gemini CLI"
evaluated_organization: "BenchHub Engineering"
staff_section: "Backend / Infrastructure"
role_in_exercise: "AI Agent Peer Programmer"
---

# HOT WASH REPORT FORM

## 1. Top Three (3) Organizational Strengths

1. **Root-Cause Driven Investigation:** 
   - *Details:* Before writing any code to patch BigQuery schemas or orchestrator failures, the team enforced a strict "investigate first, act second" policy using the `ng-investigate` mission orders. This prevented superficial fixes and exposed the underlying logical constraints of the `MERGE` statements without resorting to disruptive database DDL `ALTER TABLE` commands.

2. **Leveraging Native Capabilities (Harbor Resume & GCS Versioning):** 
   - *Details:* Rather than rebuilding failure-tracking state machines from scratch, the architecture cleanly hijacked the existing `harbor jobs resume` CLI and relied on native Google Cloud Storage (GCS) Object Versioning. This kept the `bench-hub` orchestrator code incredibly thin and delegated complex merge logic to the tools designed for it.

3. **Effective Cross-Boundary Context Management:** 
   - *Details:* The team successfully navigated a highly complex multi-layered system (FastAPI Orchestrator -> Cloud Batch -> Docker Entrypoint -> Python Sidecar -> BigQuery -> React UI) by intelligently overriding and preserving environment variables (`BENCHHUB_RUN_ID` vs `BATCH_JOB_ID`) to "trick" different layers into maintaining consistent state.

---

## 2. Top Three (3) Items Requiring Improvement

1. **Docker Container Dependency Drift:** 
   - *Details:* The initial implementation failed because the slim Python Docker container lacked the `google-cloud-sdk`. Implicit dependencies on shell tools (`gsutil cp` inside `entrypoint.sh`) must be rigorously verified against the explicitly declared Dockerfile base image during the PR authoring phase.

2. **Blind Extraction of Inline Scripts:** 
   - *Details:* When refactoring inline Python scripts out of `entrypoint.sh` into `safe_extract.py`, the team failed to account for how bash handles stdout assignment (`$()`). Because the Python script failed silently on a missing zip file, it returned an empty string, crashing the bash `mkdir` command. Extracted scripts must have strict fallback outputs or bash must handle empty variables safely.

3. **GCP API Security Side-Effects:** 
   - *Details:* The team assumed the Cloud Batch API's `get_job` method returned a 1:1 copy of the originally submitted job. In reality, GCP scrubs `secret_variables` for security reasons. Copying objects directly from Cloud APIs back into submission payloads requires defensive checks for stripped sensitive fields.

---

## 3. Hot Wash Remarks / Comments

- The `1:MANY` relationship redesign in BigQuery (`run_id` -> multiple `job_id`s) was a massive architectural win. It satisfied Cloud Batch's strict "unique job ID" constraint while giving the UI a clean way to fetch the latest attempt via `ROW_NUMBER() OVER(PARTITION)`.
- Communication and planning via Graphviz diagrams proved to be an incredibly effective way to confirm complex schema and state-machine changes before writing code.
- Local testing of Cloud Batch worker containers requires precise environment variable injection and explicit volume mapping for GCP credentials (`application_default_credentials.json`). Sudo environment variable stripping was a minor roadblock that required explicit path hardcoding to resolve.
