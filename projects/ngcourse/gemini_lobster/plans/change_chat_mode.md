### Task

The chat mode currently

1. streams all responses back into google chat
2. it spins an interactive gemini cli session locally

What I want is two things:

1. Instead of using interactive mode, invoke via none interactive mode `gemini -y -p "query"`. Store the chat history in a session file.

```json
{
  "session_id": ...,
  "messages": [
    ...
  ]
}
```

2. when returning response to chat, only the final resposne of the gemini cli session is returned (not the intermediate responses and thinking).

When user sends follow up question, we will append the new question to the session file and invoke gemini cli again. sending in the entire session as context. 

Now what happens to new sessions and multiple users?

Let's do it this way:

user can only interact with gemini via direct ping i.e @lobster in the mssage. We are going to store who pinged the lobster, and store a dedicated session file for each user.

when session is too big, we are going to summarize the previous conversation and start a new session.

### context

/usr/local/google/home/guyu/Desktop/ngcourse/gemini_lobster

### Analysis

The current implementation uses a persistent `pty` session to run an interactive `gemini` shell. This makes state management tied to the process life-cycle and difficult to manage for multiple users or "one-shot" interactions.

The goal is to move to a stateless (process-wise) but stateful (data-wise) model:
1.  **State Management**: maintain chat history in JSON files, keyed by user/thread.
2.  **Execution**: Use `gemini -y -p "..."` for each turn, passing the full context.
3.  **Output Control**: Only show the final response, suppressing intermediate tool uses or thoughts.

### Detailed Plan

#### 1. Session Management
We will implement a `SessionManager` class to handle:
-   Loading/Saving sessions from `~/.gemini/sessions/<user_id>.json`.
-   Session format:
    ```json
    {
      "user_id": "...",
      "thread_id": "...",
      "messages": [
        {"role": "user", "content": "..."},
        {"role": "model", "content": "..."}
      ],
      "last_updated": "..."
    }
    ```
-   Context window management: Summarize or truncate if history gets too long (heuristic based on message count/size).

#### 2. Chat Daemon Refactor (`chat_bridge_daemon.py`)
-   Remove `pty` based loop.
-   Implement a new main loop:
    1.  Poll for messages (using existing `input_poller` logic adapted).
    2.  On new message (`@MENTION` or direct DM):
        a.  Identify User.
        b.  Load Session.
        c.  Append User Message.
        d.  Construct Prompt (History + New Message).
        e.  Show "Thinking..." indicator.
        f.  Run `gemini -y -p "PROMPT"` with `CHAT_BRIDGE_SILENT=true`.
        g.  Capture stdout/response.
        h.  Append Model Response to Session.
        i.  Send Response to Chat.

#### 3. Output Control (`hooks/chat_hook.py`)
-   Update `chat_hook.py` to check for `CHAT_BRIDGE_SILENT` env var.
-   If `SILENT` is set:
    -   Skip visible messages for `tool_start`, `tool_output`, `thinking` events.
    -   Still allow `error` events (maybe?).
    -   Definitely send the final response (or let the daemon handle it if we capture stdout).
    -   *Correction*: If we capture stdout in the daemon, we might not need the hook to send the final response. But the hook is useful for rich formatting if `gemini` sends it.
    -   *Decision*: Let's rely on the Daemon to send the final answer from valid stdout to avoid duplicates, and mute the hook entirely for this mode, OR keep hook for errors.

#### 4. Prompt Construction
Since `gemini` CLI doesn't have a native "history file" flag visible in `help`, we will textually reconstruction the conversation:
```text
Previous conversation:
User: ...
Model: ...

Current User Input: ...
```

### Files to Modify
-   `plans/change_chat_mode.md` (this file)
-   `chat_bridge_daemon.py`: Rewrite run loop.
-   `hooks/chat_hook.py`: Add silence support.
-   `utils.py`: Add session helper functions?