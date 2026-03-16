### Instruction

'plan': Review the provided @task, write rootcause to @analysis section, add your @fix_plan and all relevant files under @files. NO CODE CHANGE.
'execute': Executes @fix_plan. If empty, stop and ask usr.

### Task

b/487688884: [BenchHub][Usability] Verify that all arguments passed via client are valid

### analysis

The issue requests validation for arguments passed by clients (CLI, Web UI) before a job is fully started to prevent rapid failures down the line. Currently, fields like `model` (which requires the format `provider/model_name`) and `eval_branch` are accepted blindly by the orchestrator and the CLI. 

If invalid values are passed, the orchestrator spawns a job and background tasks that eventually fail, wasting compute resources and confusing the user.

Entry points for these parameters:
- **CLI (`cli/cli.py`)**: `args.model` and `args.eval_branch`.
- **Orchestrator API (`orchestrator/main.py`)**: `JobRequest` model (line 206).

### fix_plan

1. **Update `JobRequest` validation (`orchestrator/main.py`)**:
   - Add a Pydantic `@field_validator("model")` to ensure the model string contains a `/` (e.g., `provider/model_name`).

2. **Add asynchronous branch validation (`orchestrator/main.py`)**:
   - In `_create_job_internal()`, before starting the job, verify the `eval_branch` exists by making a lightweight asynchronous call (e.g., via `git ls-remote` or GitHub API) against the repository. If it doesn't exist, return an `HTTPException(status_code=400)`.

3. **Enhance CLI validation (`cli/cli.py`)**:
   - In `cli/cli.py` around line 646 (where `args.model` is checked for being empty), add a check for the `provider/model_name` format. If it fails, invoke `parser.error()`.
   - Ensure the CLI gracefully handles HTTP 400 errors from the orchestrator API when `eval_branch` validation fails, displaying a friendly error to the user.

### files
- `orchestrator/main.py`
- `cli/cli.py`
