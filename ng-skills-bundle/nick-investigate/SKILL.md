---
name: nick-investigate
description: >
 Investigate a codebase problem, identify root cause and fix, then create or
 update a GitHub issue using the mission-order-template format. Returns the
 issue URL. Accepts a problem description OR an existing issue URL.
 Usage: /nick-investigate <problem-description-or-file-path-or-issue-url>
user-invocable: true
argument-hint: '<problem description, file path, or issue URL> [--repo owner/repo] [--labels bug,investigation]'
disable-model-invocation: false
allowed-tools: Bash(gh *), Bash(git *), Read, Grep, Glob, Task
---


# nick Investigate


Investigate a problem in the codebase, identify root cause and proposed fix,
then create a structured GitHub issue (or update an existing one) and return the issue URL.


## Input


`$ARGUMENTS` — One of:
- A problem description, error message, file path, or area of concern to investigate.
- A GitHub issue URL (e.g. `https://github.com/owner/repo/issues/123` or `owner/repo#123`).


Optional flags:
- `--repo owner/repo` — Target repository (default: current repo from `gh repo view`)
- `--labels label1,label2` — Comma-separated labels for the issue (default: `investigation`)


## Workflow


### Step 0 — Parse arguments and detect mode


Extract the problem description and any optional flags from `$ARGUMENTS`.


```
INPUT        = positional text (everything before first --)
REPO         = --repo value or detect via `gh repo view --json nameWithOwner -q .nameWithOwner`
LABELS       = --labels value or "investigation"
```


**Mode detection:** Determine whether INPUT is an existing GitHub issue:
- If INPUT matches a GitHub issue URL pattern (`https://github.com/.../issues/\d+`) or shorthand (`owner/repo#\d+`), set `MODE=update` and extract the issue number.
- Otherwise, set `MODE=create` and treat INPUT as the problem description.


If `MODE=update`:
1. Fetch the existing issue with `gh issue view <number> --repo "$REPO" --json title,body,labels`.
2. Store the original issue body as `ORIGINAL_BODY`.
3. Extract the problem description from `ORIGINAL_BODY` — this is your investigation target.


### Step 1 — Investigate


Use Read, Grep, Glob, and Task (subagents) to understand the problem:


1. **Locate** — Find relevant files, error origins, related code paths.
2. **Trace** — Follow the execution path to understand how the problem manifests.
3. **Root-cause** — Identify the fundamental cause, not just symptoms.
4. **Fix plan** — Determine the minimal, surgical fix.


Spend the majority of effort here. Do NOT skip to issue creation without thorough understanding.


### Step 2 — Draft the issue body


Read the mission-order-template from `docs/mission-order-template.md` in the repo root. Structure the investigation body using that template.


If `MODE=update`, the final body MUST preserve the original description under a "Context" section at the top:


````markdown
## Original Context


> <ORIGINAL_BODY — reproduced verbatim as a blockquote>


---


## Investigation Summary
...
````


If `MODE=create`, start directly with the Investigation Summary.


The investigation sections are the same for both modes:


```markdown
## Investigation Summary


**Root Cause:** <1-2 sentence explanation of the fundamental problem>


**Impact:** <What breaks, who is affected, severity>


**Reproduction:** <Steps or conditions to trigger the issue, if applicable>


## Order


(Fill every field from docs/mission-order-template.md — mark N/A if not applicable)


**Intent:** <Why we're doing this and the desired end state>


**Constraints:** <Forbidden actions>


**Done-when:**
- [ ] <Verifiable criterion 1>
- [ ] <Verifiable criterion 2>


**Resources:**
- <File paths, docs, related issues>


**ROE:** <Read-only / write / deploy. What requires approval>


**Handoff:** Return format below — no freeform.


## Fix Plan


1. <Step 1 — file:line — what to change and why>
2. <Step 2 — file:line — what to change and why>


## Related Files


| File | Role |
|------|------|
| `path/to/file.ts:42` | <Why this file is relevant> |


## Handoff Schema


```
status:      complete | blocked | partial
result:      what was done
artifacts:   [files, URLs, outputs]
deviations:  [departures from plan + why]
concerns:    [risks, unknowns]
```
```


### Step 3 — Create or update the issue


**If `MODE=create`:**


```bash
gh issue create \
 --repo "$REPO" \
 --title "<concise title>" \
 --label "$LABELS" \
 --body-file /tmp/nick-investigate-issue.md
```


Capture the returned issue URL.


**If `MODE=update`:**


```bash
gh issue edit <NUMBER> \
 --repo "$REPO" \
 --body-file /tmp/nick-investigate-issue.md
```


Add the investigation labels if not already present:


```bash
gh issue edit <NUMBER> --repo "$REPO" --add-label "$LABELS"
```


The issue URL is `https://github.com/$REPO/issues/<NUMBER>`.


### Step 4 — Return the issue URL


Print the issue URL as the final output. Format:


```
ISSUE_URL=<url>
```


## Rules


- **Investigate first, write second.** Never create/update an issue without understanding root cause.
- **Be specific.** File paths with line numbers, not vague references.
- **Minimal fix plans.** Only what's necessary — no refactoring tangents.
- **One issue per problem.** If investigation reveals multiple unrelated issues, create separate issues.
- **Preserve original context.** When updating an existing issue, the original description MUST be preserved verbatim in a blockquote under "Original Context". Never discard or paraphrase the reporter's words.
