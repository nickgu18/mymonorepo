### Instruction

'plan': Review the provided @task, write rootcause to @analysis section, add your @fix_plan and all relevant files under @files. NO CODE CHANGE.
'execute': Executes @fix_plan. If empty, stop and ask usr.

### Task

Review and address comments on PR #20 in the `harbor` repository.
The PR adds support for evaluating specific commits and tags in the Gemini CLI agent.
Reviewers have requested changes, specifically regarding validation of mutually exclusive arguments (`branch`, `commit`, `tag`) and potential inconsistencies in git logic.

### analysis

I have retrieved the inline review comments using `gh api repos/googlecloud-appeco-incubator/harbor/pulls/20/comments`.
The key feedback points are:

1.  **Validation (High Priority)**:
    *   **File**: `src/harbor/agents/installed/gemini_cli.py`
    *   **Comment**: "To avoid ambiguity and unexpected behavior, it's best to enforce that only one of `branch`, `commit`, or `tag` can be specified."
    *   **Action**: Add validation in `__init__` to raise `ValueError` if more than one of these arguments is provided.

2.  **Git Logic Inconsistency (High Priority)**:
    *   **File**: `src/harbor/agents/installed/install-gemini-cli.sh.j2`
    *   **Comment**: "The logic for checking out a branch here is inconsistent with the host-side preparation in `_prepare_host_repo`. The host-side logic performs a `git pull` to ensure the latest code is used, but this script only performs a `checkout`. This could lead to using stale code when building inside the container. To ensure consistency, a `git pull` should be added."
    *   **Action**: Update the installation script to perform `git pull origin {{ branch }}` after checking out the branch.
    *   **Note**: `silviojr` asked "If we are already using _prepare_host_repo(), do we still need this part of the code?". The answer is likely yes, because `_prepare_host_repo` is for host-side caching/bundling (optimization), while the installation script runs inside the container. If the optimization is skipped or fails, the container needs to be able to build from source itself. However, ensuring consistency is good practice.

3.  **Test Update (Medium Priority)**:
    *   **File**: `tests/unit/agents/installed/test_gemini_cli.py`
    *   **Comment**: "This test initializes the agent with both `commit` and `tag` arguments. With the recommended validation to allow only one of `commit`, `tag`, or `branch` at a time, this test will fail. It would be better to split this into two separate, more focused tests: one for `commit` and one for `tag`."
    *   **Action**: Split `test_init_with_commit_and_tag` into `test_init_with_commit` and `test_init_with_tag`. Add a new test case `test_init_with_multiple_versions_raises_error` to verify the validation logic.

### fix_plan

1.  **Modify `src/harbor/agents/installed/gemini_cli.py`**:
    *   In `__init__`, add validation to ensure mutual exclusivity of `branch`, `commit`, and `tag`.
    *   Use the logic: `if sum(p is not None for p in [branch, commit, tag]) > 1: raise ValueError(...)`. Note: `branch` defaults to `None` in `__init__` arguments, but the class might have a default. Need to check if `self.branch()` returns a default if not provided. The comment suggests checking `self.branch()`, `self._commit`, `self._tag`.

2.  **Modify `src/harbor/agents/installed/install-gemini-cli.sh.j2`**:
    *   Add `git pull origin {{ branch }}` after `git checkout {{ branch }}` to ensure the latest code is used, matching host-side behavior.

3.  **Modify `tests/unit/agents/installed/test_gemini_cli.py`**:
    *   Remove `test_init_with_commit_and_tag`.
    *   Add `test_init_with_commit`.
    *   Add `test_init_with_tag`.
    *   Add `test_init_with_multiple_versions_raises_error` (testing combinations like branch+commit, commit+tag, etc.).

4.  **Verify**: Run the tests locally using `make test` (or `pytest` specifically for harbor).

5.  **Push**: Push the changes to the PR branch.

6.  **Document**: Update `projects/bench-hub/GEMINI.md` with learnings about mutual exclusivity validation and git consistency.

### files

projects/harbor/src/harbor/agents/installed/gemini_cli.py
projects/harbor/src/harbor/agents/installed/install-gemini-cli.sh.j2
projects/harbor/tests/unit/agents/installed/test_gemini_cli.py