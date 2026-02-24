### Instruction

if mode is 'plan': Review the provided @task, write rootcause to @analysis section, add your @fix_plan and all relevant files under @files. NO CODE CHANGE.
if mode is 'execute': If fix_plan empty, stop and ask usr. Execute fix_plan

### Task

Project Design

**goal**:
1. Support multiple users and help them schedule meetings based on their calendar (multi-tenancy)

**design**:
1. User can access our appscript project from google sheet deployed as an web app. Give us authentication to access user's google calendar and google mail.
2. Every 5 minutes, our script will pull user email recieved in the past 5 minutes, check if any email is forwarded to useremail+meeting-scheduler@gmail.com
3. The appscript will send email to useremail+meeting-scheduler@gmail.com to ADK hosted on cloud run to determine
  1. If the email is a meeting request
  2. If the email is a meeting response
  3. If the email is a meeting cancellation
4. If the email is a meeting request
  1. Cloud Run ADK agent will call appscript endpoint to get user's calendar and determine the best time to schedule the meeting
  2. Clood RUn ADK agent will create draft email in gmail with proposed meeting time

**task**:
review my design and determine if it's possible. what are the key technical assumptions to verify?

### analysis

The proposed design is technically feasible but has a significant architectural complexity at step 4.1.

#### Question: Do we really need AppScript?
**Short Answer:** No, but removing it increases complexity by 10x.

**Detailed Trade-off:**
1.  **Authentication (The biggest specific reason)**:
    *   **With AppScript:** Auth is handled natively. The user runs the script, approves permissions, and `ScriptApp.getOAuthToken()` gives you a valid token. Zero infrastructure required.
    *   **Without AppScript (Pure Cloud Run):** You must build a full "Log in with Google" OAuth flows. You need to:
        *   Register an OAuth Client in GCP.
        *   Build a frontend to redirect users to Google.
        *   Build a backend callback to exchange auth codes for Refresh Tokens.
        *   **Securely store** these Refresh Tokens (Database + Encryption).
        *   Handle token rotation and expiration.
2.  **Triggers/Scheduling**:
    *   **With AppScript:** `ScriptApp.newTrigger().timeBased()` allows every user to have their own "cron job" for free.
    *   **Without AppScript:** You need a centralized Cloud Scheduler/Task Queue that wakes up every 5 minutes, iterates through ALL users in your database, refreshes their tokens, and checks their emails. This is a much heavier backend architecture.

**Conclusion:** For a prototype or internal tool, AppScript is the "cheat code" that bypasses weeks of authentication and infrastructure work. I strongly recommend keeping it for version 1.

#### Question: How does Multi-tenancy work?
**Q: Do we query all users periodically?**
**A:** No. In AppScript (Web App), we don't have a central "Master Script" that loops through all users.
Instead, when User A visits the Web App, the script installs a **Trigger** specifically for User A.
*   User A's trigger runs as User A.
*   User B's trigger runs as User B.
They are completely isolated. It's like every user has their own personal server. We don't need to "store" their email to query it later; their personal trigger *is* the query mechanism.

**Q: What happens when multiple users authenticate?**
**A:**
1.  **Isolation**: They are completely separate. User A cannot see User B's properties or tokens.
2.  **Concurrency**: Google handles the scaling. If 100 users have triggers firing at 9:00 AM, Google spins up 100 isolated instances.
3.  **Data Storage**: We can use `PropertiesService.getUserProperties()` to store data specific to that user.
    *   **Crucial for Search**: You are correct, to search `to:user@domain.com+alias`, we need `user@domain.com`.
    *   **Implementation**: On first run, we capture `Session.getActiveUser().getEmail()` and store it in `UserProperties`. The trigger then reads this stored email to construct the specific search query `to:${storedEmail}+meeting-scheduler@...`.

**Q: Can we store user emails to BigQuery in the backend?**
**A:** Yes, absolutely.
*   **Mechanism**: Apps Script sends the email + metadata to Cloud Run. Cloud Run inserts/updates the row in a BigQuery table.
*   **Use Case**: This is excellent for analytics (e.g., "Total Active Users") and central visibility, even though the *execution loop* remains distributed in Apps Script triggers.



#### Original Analysis
1.  **Multi-tenancy**: Using a Web App deployment allows users to authorize the script effective execute as "User accessing the web app". Time-driven triggers (every 5 mins) can be programmatically created for each user, which is scalable within AppScript limits (20 triggers/user).
2.  **Email Forwarding**: Monitoring `useremail+meeting-scheduler@gmail.com` using `GmailApp.search('to:me+meeting-scheduler@gmail.com')` is a valid approach that avoids checking every single email. This relies on the user properly mapping the alias or just using it directly.
3.  **Cloud Run -> AppScript (Step 4.1)**: This is the critical friction point. Calling AppScript *back* from Cloud Run (to access calendar/create draft) requires the AppScript to be deployed as an API executable with correct OAuth setup, which is complex and prone to latency/timeout issues.
    -   **Optimization**: Instead of Cloud Run calling AppScript back, AppScript should pass a temporary OAuth token (`ScriptApp.getOAuthToken()`) to Cloud Run in the initial payload (Step 3). Cloud Run can then use this token to call Google Calendar API and Gmail API *directly* on behalf of the user. This eliminates the need for Cloud Run to call AppScript, simplifies the architecture (unidirectional flow), and improves performance.


### fix_plan

1.  **Verify Alias Search**: User reported `to:me+alias` unreliable, but full address (e.g., `nick+ngo@google.com`) works. We will update the search query to use the specific full email address or `deliveredto:` header for reliability.
2.  **Prototype Token Passing**: Create a **Proof of Concept (POC)** structure where AppScript passes `ScriptApp.getOAuthToken()` to the Cloud Run endpoint. A POC is a small, focused implementation to verify technical feasibility.
3.  **Prototype ADK Actions**: Implement a minimal Python service (Cloud Run) that accepts the token and successfully calls Google Calendar API (list events) and Gmail API (create draft).
4.  **End-to-End Test**: detailed flow:
    -   Script triggers -> Finds Email -> Sends content + Token to Cloud Run.
    -   Cloud Run -> Analyzes -> Checks Calendar (direct API) -> Creates Draft (direct API).



### files

- `meeting-pro-g/appscript/Code.js`
- `meeting-pro-g/appscript/appsscript.json`
- `meeting-pro-g/adk/main.py`
- `meeting-pro-g/adk/requirements.txt`
- `meeting-pro-g/adk/Dockerfile`