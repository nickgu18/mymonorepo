# Meeting Project MVP Design

## Architecture

[View Architecture Diagram (HTML)](architecture.html)


## Components

### 1. Frontend / Trigger (AppScript)
*   **Role**: The "sensor" and "authorizer".
*   **Responsibility**:
    *   **Execution Context**: Runs strictly as the user (`executeAs: USER_ACCESSING`). When a trigger fires, it runs **as the user who installed it**.
    *   **Token Retrieval**: Calls `ScriptApp.getOAuthToken()`. This returns a standard Google OAuth 2.0 Access Token for the *current effective user* (the trigger owner).
    *   **Scopes**: We must declare scopes (Calendar, Gmail) in `appsscript.json`. The token will include these permissions.
    *   **Action**: POSTs the payload to Cloud Run:
        *   `token` (OAuth Access Token)
        *   `user_email`
        *   `message_id` (ID of the specific email)
        *   `thread_id` (ID of the thread for context retrieval)
        *   `email_content` (Body/Snippet)


> initial_pass
appscript: meeting-pro-g/appscript
A. Fetch relevant emails (Search `to:TOKEN_EMAIL+meeting-scheduler@...`)
   > *Critique*: "Fetch 10 emails" is risky. If the user got 20 unrelated emails, we miss the scheduling ones. Search is mandatory.

B. Creates a landing page for user to configure settings - trigger duration, preferred meeting length, timezone (default EST)
C. Sends (email_content, message_id, thread_id, token, user_email) to cloudrun

C. Deploys as webapp

### 2. Backend Agent (Cloud Run + ADK)
*   **Role**: The "brain".
*   **Stack**: Python, ADK (GenAI agent framework).
*   **Responsibility**:
    *   **Intent Recognition**: Is this email asking for a meeting?
    *   **RAG / Context**: What is the user's availability? (Calls Google Calendar API).
    *   **Action**: Drafts a reply.
    *   **Analytics**: Logs usage to BigQuery.

> initial_pass
cloudrun: meeting-pro-g/cloudrun/adk
exposes endpoint for processing email.

Agent Logic:

- root agent
  - email triage agent: determine intent
    - based on messageid and threadid (email thread)
  - scheduling agent:
    - if intent is cancel meeting
      - cancel calendar event
    - if intent is confirm meeting
      - create calendar event
    - if intent is (re)schedule meeting
      - pull google calendar data for the proposed date or date range
      - propose new time(s)
      - draft email to ask for confirmation
    - if intent is unknown
      - draft email to ask for clarification
  - author agent:
    - polish the email draft style based on user preferences
  - creates email draft

### 3. Storage (BigQuery)
*   **Role**: The "memory" (Long-term).
*   **Schema**: `requests_table`
    *   `timestamp`
    *   `user_email`
    *   `thread_id`
    *   `intent_classification` (e.g., "new_meeting")
    *   `status` (e.g., "draft_created")

### SQL Schema
```sql
CREATE OR REPLACE TABLE `meetingprog.requests_table` (
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    user_email STRING NOT NULL,
    thread_id STRING,
    intent_classification STRING,
    status STRING,
    metadata JSON
)
PARTITION BY DATE(timestamp);
```


## Security & Privacy (Crucial)

### Token Management
*   **Refresh Tokens**: We **DO NOT** handle them. AppScript manages the user's authorization lifecycle internally. We never see the refresh token.
*   **Access Tokens**: We pass the short-lived (1 hour) access token to Cloud Run.
    *   **Storage**: We **NEVER** store access tokens in BigQuery or logs. They are transient.
    *   **Usage**: Cloud Run keeps the token in memory only for the duration of the request.

### Data Privacy
*   **Email Content**: We analyze email content in memory. We should decide if we want to store the *full body* in BigQuery or just the *metadata* (recommended for privacy).


## AI Evaluation Strategy

We will evaluate the ADK Agent capabilities on two levels:

### Level 1: Offline Evaluation (Golden Sets)
*   **Dataset**: A curated set of 50 mocked emails (20 requests, 20 spam, 10 rescheduling).
*   **Metric**:
    *   **Intent Accuracy**: Did we correctly identify "Meeting Request" vs "Spam"?
    *   **Slot Quality**: Did the agent pick a time that was actually free? (Requires mocked calendar state).
*   **Pipeline**:
    *   Run `pytest` with a mock ADK runner against the Golden Set.
    *   Assert `predicted_intent == true_intent`.

### Level 2: Online Evaluation (User Feedback)
*   **Metric**: **Draft Acceptance Rate**.
    *   If we create a draft and the user *sends* it (with < 20% edit distance), it's a **Success**.
    *   If the user *deletes* the draft, it's a **Failure**.
*   **Implementation**:
    *   The Agent embeds a hidden ID or tag in the Draft.
    *   A nightly job checks if that Draft ID was sent or deleted.
