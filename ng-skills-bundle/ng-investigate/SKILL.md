---
name: legion-investigate
description: >
 Investigate a codebase problem, identify root cause and fix, then create or
 update a Buganizer issue using the mission-order-template format. Returns the
 issue URL. Accepts a problem description OR an existing Buganizer issue URL/ID.
 Usage: /legion-investigate <problem-description-or-file-path-or-bug-id>
user-invocable: true
argument-hint: '<problem description, file path, or Buganizer issue ID/URL> [--component component_id]'
disable-model-invocation: false
allowed-tools: Bash(gemini *), Bash(git *), Read, Grep, Glob, Task
---

# Legion Investigate

Investigate a problem in the codebase, identify root cause and proposed fix,
then create a structured Buganizer issue (or update an existing one) and return the issue URL.

## Input

`$ARGUMENTS` — One of:
- A problem description, error message, file path, or area of concern to investigate.
- A Buganizer issue URL (e.g. `https://issuetracker.google.com/issues/12345678`) or ID (e.g. `b/12345678` or `12345678`).

Optional flags:
- `--component id` — Target Buganizer component ID (if creating a new bug).

## Workflow

### Step 0 — Parse arguments and detect mode

Extract the problem description and any optional flags from `$ARGUMENTS`.

```
INPUT        = positional text (everything before first --)
COMPONENT    = --component value (if provided)
```

**Mode detection:** Determine whether INPUT is an existing Buganizer issue:
- If INPUT matches a Buganizer issue URL pattern or shorthand (`b/\d+` or just digits like `12345678`), set `MODE=update` and extract the bug number.
- Otherwise, set `MODE=create` and treat INPUT as the problem description.

If `MODE=update`:
1. Fetch the existing bug details using the Gemini CLI:
   `gemini -y -p "Read bug <number> and output its full title and description"`
2. Store the original bug description as `ORIGINAL_BODY`.
3. Extract the problem description from `ORIGINAL_BODY` — this is your investigation target.

### Step 1 — Investigate

Use Read, Grep, Glob, and Task (subagents) to understand the problem:

1. **Locate** — Find relevant files, error origins, related code paths.
2. **Trace** — Follow the execution path to understand how the problem manifests.
3. **Root-cause** — Identify the fundamental cause, not just symptoms.
4. **Fix plan** — Determine the minimal, surgical fix.

Spend the majority of effort here. Do NOT skip to issue creation without thorough understanding.

### Step 2 — Draft the investigation body

Read the mission-order-template from `template.md` in the repo root (if it exists). Structure the investigation body using that template.

If `MODE=update`, the final body MUST preserve the original description under a "Context" section at the top (or just reference it), but since Buganizer appends comments, you can just write the Investigation Summary as a new comment.

The investigation body should look like this:

```markdown
## Investigation Summary

**Root Cause:** <1-2 sentence explanation of the fundamental problem>

**Impact:** <What breaks, who is affected, severity>

**Reproduction:** <Steps or conditions to trigger the issue, if applicable>

## Order

(Fill relevant fields — mark N/A if not applicable)

**Intent:** <Why we're doing this and the desired end state>

**Constraints:** <Forbidden actions>

**Done-when:**
- [ ] <Verifiable criterion 1>
- [ ] <Verifiable criterion 2>

**Resources:**
- <File paths, docs, related issues>

**Fix Plan:**
1. <Step 1 — file:line — what to change and why>
2. <Step 2 — file:line — what to change and why>

## Related Files

| File | Role |
|------|------|
| `path/to/file.ts:42` | <Why this file is relevant> |

## Handoff Schema

status:      complete | blocked | partial
result:      what was done
artifacts:   [files, URLs, outputs]
deviations:  [departures from plan + why]
concerns:    [risks, unknowns]
```

Save this content to `/tmp/legion-investigate-issue.md`.

### Step 3 — Create or update the Buganizer issue

**If `MODE=create`:**

Use the Gemini CLI to create the bug. Provide the component ID if you have it (otherwise the agent might need to deduce it or ask):

```bash
# Example if component is known:
gemini -y -p "Create a bug in Buganizer in component <COMPONENT> with title '<concise title>' and description exactly matching the contents of file /tmp/legion-investigate-issue.md. Return the created bug ID and URL."

# If component is not provided:
gemini -y -p "Create a bug in Buganizer with title '<concise title>' and description exactly matching the contents of file /tmp/legion-investigate-issue.md. Return the created bug ID and URL."
```

**If `MODE=update`:**

Use the Gemini CLI to append your investigation as a comment:

```bash
gemini -y -p "Add comment to bug <NUMBER> with the exact content of file: /tmp/legion-investigate-issue.md"
```

### Step 4 — Return the issue URL

Print the Buganizer issue URL as the final output. Format:

```
ISSUE_URL=https://issuetracker.google.com/issues/<NUMBER>
```

## Rules

- **Investigate first, write second.** Never create/update an issue without understanding root cause.
- **Be specific.** File paths with line numbers, not vague references.
- **Minimal fix plans.** Only what's necessary — no refactoring tangents.
- **One issue per problem.** If investigation reveals multiple unrelated issues, create separate issues.
