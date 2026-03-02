### Instruction

'plan': Review the provided @task, write rootcause to @analysis section, add your @fix_plan and all relevant files under @files. NO CODE CHANGE.
'execute': Executes @fix_plan. If empty, stop and ask usr.

### Task

Enable `g3lobster` to send direct messages (DMs) to individual users by email (e.g., `alexyan@google.com`), instead of only responding in a configured space.

### analysis

The current `g3lobster` implementation is designed as a "Chat Bridge" that polls a single configured space for @mentions and responds in-thread.

**Root Causes for lack of DM support:**
1.  **Space-Centric Design:** The `ChatBridge` class is initialized with a single `space_id` and focuses on that context.
2.  **No User Lookup:** There is no logic to resolve an email address (like `alexyan@google.com`) to a Google Chat User resource name (`users/{id}`).
3.  **Missing DM Creation Logic:** The `spaces.setup` method with `spaceType="DIRECT_MESSAGE"` is not utilized.

**Technical Constraints:**
*   **User Resolution:** The Google Chat API `users.get` or `users.list` often requires specific scopes (`chat.users.readonly`). The current scopes in `auth.py` are limited to messages/spaces/memberships.
*   **Email Support:** Using an email directly in `spaces.setup` `memberships` is supported for Google Workspace users in the same organization, but we must verify if the current OAuth scopes allow this resolution.
*   **API Usage:** We should use `spaces.setup` (or `findDirectMessage`) to create the DM, which is idempotent (returns existing space if present).

### fix_plan

1.  **Update `g3lobster/chat/auth.py`**:
    *   Add `https://www.googleapis.com/auth/chat.users.readonly` to `SCOPES` if necessary for robust user lookup (optional, try without first).
    *   *Self-Correction*: Changing scopes requires re-authentication (deleting `token.json`). We should try to work with existing scopes first (by listing members of known spaces or using email directly in `spaces.setup` which often works for intra-domain).

2.  **Create `g3lobster/chat/dm.py`**:
    *   Logic to resolving a user (try: direct API use, or scan existing spaces/DMs).
    *   Logic to ensure a DM space exists (`spaces.setup`).
    *   Logic to send a message to that space.

3.  **Create `g3lobster/tools/dm.py` (CLI Tool)**:
    *   A standalone script to execute the DM sending.
    *   Args: `--email` (or `--user`), `--message`.

4.  **Verification**:
    *   Run the tool with `alexyan@google.com`.
    *   If specific user scopes are needed and missing, we will guide the user to re-auth.

### files

*   `g3lobster/chat/dm.py` (New)
*   `g3lobster/tools/dm.py` (New)
*   `g3lobster/chat/auth.py` (Modify scopes if needed, but try to avoid)
