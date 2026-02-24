### Instruction

if mode is 'plan': Review the provided @task, write rootcause to @analysis section, add your @fix_plan and all relevant files under @files. NO CODE CHANGE.
if mode is 'execute': If fix_plan empty, stop and ask usr. Execute fix_plan

### Task

meeting-pro-g/docs/mvp.md describes plan to build ADK agent.
Build out the ADK agent. and write down plans for deploying this to cloud run using gcloud cli.

### analysis

The ADK (Agent Development Kit) agent needs to act as the "Brain" of the meeting scheduler.
It receives a payload from AppScript (`token`, `message_id`, `thread_id`, `user_email`) and decides on an action.

**Core Components Defined in MVP:**
1.  **Architecture**: Flask/FastAPI app hosting ADK agents.
2.  **Agents**:
    *   `RootAgent` (Router)
    *   `EmailTriageAgent` (Intent Classification)
    *   `SchedulingAgent` (Calendar Operations)
    *   `AuthorAgent` (Drafting Emails)
3.  **Integrations**:
    *   Google Calendar API (via passed Token)
    *   Gmail API (via passed Token)
    *   BigQuery (Analytics Logging)

**Key Constraints**:
*   Must accept `thread_id` to fetch full context.
*   Must **NOT** store tokens (use immediate memory only).
*   Must output a JSON response to AppScript (success/fail).


### fix_plan

1.  **Scaffold Project**:
    *   Create `main.py` (Entrypoint, API handling).
    *   Create `requirements.txt` (adk, flask, google-api-python-client, google-cloud-bigquery).
    *   Create `Dockerfile` for Cloud Run.

2.  **Implement Agents (`agents.py`)**:
    *   Define `TriageAgent`: Uses Logic to classify intent.
    *   Define `SchedulingAgent`:
        *   Tool: `fetch_calendar_events(token, time_range)`
        *   Tool: `find_free_slots(events)`
        *   Tool: `create_calendar_event(token, details)` (Draft/Tentative mode).
    *   Define `AuthorAgent`:
        *   Tool: `create_gmail_draft(token, reply_body, thread_id)`

3.  **Implement Logic (`main.py`)**:
    *   `/analyze` endpoint.
    *   Fetch full thread using `thread_id` and `token`.
    *   Pass thread history to `TriageAgent`.
    *   Route to `SchedulingAgent` or `AuthorAgent` based on intent.
    *   Log metadata to BigQuery.

4.  **Deployment Scripts**:
    *   `deploy.sh`: `gcloud run deploy` command references.



### files

- `meeting-pro-g/cloudrun/adk/main.py`
- `meeting-pro-g/cloudrun/adk/agents.py`
- `meeting-pro-g/cloudrun/adk/tools.py`
- `meeting-pro-g/cloudrun/adk/requirements.txt`
- `meeting-pro-g/cloudrun/adk/Dockerfile`
- `meeting-pro-g/cloudrun/adk/deploy.sh`