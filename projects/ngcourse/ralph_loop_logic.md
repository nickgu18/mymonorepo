# Ralph Loop Logic Explained

The **Ralph Loop** is a self-referential feedback loop implemented as a plugin for Claude Code. It forces the agent to iterate on a task by intercepting its attempt to exit and feeding the original prompt back to it, until specific completion criteria are met.

Here is the logic explained in ASCII art:

```ascii
                                 (User runs /ralph-loop)
                                            │
                                            ▼
                                  ┌───────────────────┐
                                  │   SETUP SCRIPT    │
                                  │(setup-ralph-loop) │
                                  └─────────┬─────────┘
                                            │ Writes
                                            ▼
                                 ┌─────────────────────┐
                                 │ STATE FILE (.md)    │◄───┐
                                 │ - iteration: 1      │    │
                                 │ - max_iterations: N │    │
                                 │ - promise: "DONE"   │    │
                                 │ - PROMPT: "Task..." │    │
                                 └──────────┬──────────┘    │
                                            │               │
            ┌───────────────────────────────┘               │
            │                                               │
            │          THE RALPH LOOP                       │
            │                                               │
            ▼                                               │
    ╔══════════════╗                                        │
    ║    CLAUDE    ║                                        │
    ║   (Worker)   ║                                        │ Update
    ╚══════╤═══════╝                                        │ State
           │                                                │(Inc Iteration)
           │ Performs Task                                  │
           │                                                │
           │ "I am done."                                   │
           │ (Attempts Exit)                                │
           ▼                                                │
    ┌──────────────┐                                        │
    │  STOP HOOK   │                                        │
    │(hooks/stop.sh)────────────────────────────────────────┘
    └──────┬───────┘
           │
           │ Intercepts Exit & Checks Criteria:
           │
           ├─ 1. Is Iteration >= Max? ──────────────┐
           │                                        │
           ├─ 2. Is <promise>MATCH</promise>? ──────┤
           │     (Scans last transcript msg)        │
           │                                        │
           ▼                                        ▼
        [NO]                                      [YES]
    (Conditions met?)                         (Conditions met?)
           │                                        │
           │                                        │
   BLOCK EXIT                                   ALLOW EXIT
   Returns:                                         │
   {                                                │
     "decision": "block",                           │
     "reason": "ORIGINAL_PROMPT"                    │
   }                                                │
           │                                        │
           │                                        ▼
           └───────────────────────────────> (LOOP FINISHED)
```

## Key Components

1.  **Setup (`setup-ralph-loop.sh`)**:
    *   Initializes the persistent state file (`.claude/ralph-loop.local.md`) with the **original prompt** and **completion criteria** (max iterations or a specific "promise" string).
    *   This file acts as the "memory" of the loop configuration.

2.  **The Hook (`hooks/stop-hook.sh`)**:
    *   This is the core engine. It runs every time Claude tries to exit.
    *   It reads the state file and the current transcript.
    *   **Strict Verification**: If a `--completion-promise` is set, it uses `grep`/`perl` to extract the content inside `<promise>...</promise>` tags from Claude's last message and ensures it **exactly matches** the required string.

3.  **The Feedback**:
    *   If criteria are *not* met, the hook returns `decision: "block"`.
    *   Crucially, it sets `"reason": "ORIGINAL_PROMPT"`. This effectively "re-types" the user's original request into the context, forcing Claude to look at its previous work (files, git history) and try again.
