# Support Gemini CLI Plan

## Goal
Modify the SDK to support `gemini` CLI as the backend transport, enabling `gemini -y -p "query"` execution.

## User Review Required
> [!IMPORTANT]
> This plan involves "aggressive reduction" of Claude-specific features that don't apply to Gemini.
> We will focus on a simple request-response model first.

## Proposed Changes

### Transport Layer
#### [NEW] `src/claude_agent_sdk/_internal/transport/gemini_cli.py`
- Implement `GeminiCLITransport` inheriting from `Transport`.
- Uses `gemini` command instead of `claude`.
- construct command with `['gemini', '-y', '-p', prompt]`.
- Output handling:
    - If `gemini` outputs JSON stream, we can reuse some logic.
    - If `gemini` outputs raw text, we need a simple adapter to wrap it in a `Message` object.

### Client/Query Layer
#### [MODIFY] `src/claude_agent_sdk/query.py`
- Allow selecting `GeminiCLITransport` via options or auto-detection.
- Maybe add `GeminiAgentOptions`?

#### [MODIFY] `src/claude_agent_sdk/types.py`
- Add `GeminiAgentOptions` or generalize `ClaudeAgentOptions`.
- For now, we might just reuse `ClaudeAgentOptions` but ignore unrelated fields, or creating a simpler `AgentOptions` class.

### Clean up
- Remove strict dependency on `claude` binary presence checks if using Gemini.

## Verification Plan
### Automated Tests
- Create a test that mocks `gemini` CLI output (since we might not have a real responding `gemini` agent in CI environment, but locally we do).
- Run `query("hello")` with Gemini transport.

### Manual Verification
- Run a script that calls `query.py` with `gemini` transport.
- Verify it calls `gemini -y -p "..."` and returns result.