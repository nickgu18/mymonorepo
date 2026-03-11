import re

# 1. Patch orchestrator/main.py
with open("orchestrator/main.py", "r") as f:
    content = f.read()

# Add missing copy import if needed
if "import copy" not in content:
    content = content.replace("import io", "import io\nimport copy")

# Add auth check and update signature
auth_check_code = """
        # 1.5. Authorization check
        user_email = request.headers.get("X-Goog-Authenticated-User-Email")
        if user_email:
            email_parts = user_email.split(":")
            clean_email = email_parts[-1] if len(email_parts) > 1 else user_email
            job_user = job_data.get("hub_user")
            if (
                job_user
                and clean_email != job_user
                and not clean_email.endswith("@google.com")
            ):
                raise HTTPException(
                    status_code=403, detail="Not authorized to modify this job"
                )
        elif os.environ.get("K_SERVICE"):  # Prod environment should have this header
            logger.warning(
                f"Missing X-Goog-Authenticated-User-Email for heal_job on {job_id}"
            )
"""

content = re.sub(
    r"def heal_job\(job_id: str\):",
    "def heal_job(job_id: str, request: Request):",
    content,
)

content = re.sub(
    r"(job_data = bq_client\.get_job\(job_id\)\n\s+if not job_data:\n\s+raise HTTPException\(\n\s+status_code=404, detail=f\"Job \{job_id\} not found in BigQuery\"\n\s+\))",
    r"\1\n" + auth_check_code,
    content,
)

# Fix copy.deepcopy
old_copy_code = """        # Deep copy the first task group to avoid side-effects on old_job
        new_task_group = batch_v1.TaskGroup(old_job.task_groups[0])
        new_task_spec = batch_v1.TaskSpec(new_task_group.task_spec)
        new_runnable = batch_v1.Runnable(new_task_spec.runnables[0])
        new_container = batch_v1.Runnable.Container(new_runnable.container)

        # Re-construct the hierarchy
        new_runnable.container = new_container
        new_task_spec.runnables = [new_runnable]
        new_task_group.task_spec = new_task_spec
        new_job.task_groups = [new_task_group]"""

new_copy_code = """        # Deep copy the first task group to avoid side-effects on old_job
        new_task_group = copy.deepcopy(old_job.task_groups[0])
        new_job.task_groups = [new_task_group]"""

content = content.replace(old_copy_code, new_copy_code)

with open("orchestrator/main.py", "w") as f:
    f.write(content)

print("Patched orchestrator/main.py")

# 2. Patch worker/entrypoint.sh
with open("worker/entrypoint.sh", "r") as f:
    sh_content = f.read()

safe_extract_code = """    mkdir -p tmp_extract
    # Use python to safely extract to prevent Zip Slip and read run_id dynamically
    python3 -c "
import zipfile
import os
import json
import sys

extract_dir = 'tmp_extract'
zip_path = 'raw_logs.zip'

try:
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.namelist():
            member_path = os.path.abspath(os.path.join(extract_dir, member))
            if member_path.startswith(os.path.abspath(extract_dir)):
                zf.extract(member, extract_dir)
except Exception as e:
    print(f'Extraction failed: {e}', file=sys.stderr)
    sys.exit(1)

# Read RUN_FOLDER_NAME from config.json to avoid fragility
run_folder_name = 'eval-' + os.environ.get('RESUME_FROM_RUN_ID', 'unknown')
config_path = os.path.join(extract_dir, 'config.json')
if os.path.exists(config_path):
    try:
        with open(config_path, 'r') as cf:
            config = json.load(cf)
            if 'run_id' in config:
                run_folder_name = config['run_id']
            elif 'eval_id' in config:
                run_folder_name = config['eval_id']
    except Exception as e:
        print(f'Failed to read config.json: {e}', file=sys.stderr)

with open('run_folder_name.txt', 'w') as f:
    f.write(run_folder_name)
" || { report_early_failure "Failed to safely extract previous logs."; exit 1; }
    
    RUN_FOLDER_NAME=\$(cat run_folder_name.txt)
    rm run_folder_name.txt
    
    mkdir -p \"\$RUN_FOLDER_NAME\"
    cp -a tmp_extract/. \"\$RUN_FOLDER_NAME/\"
"""

old_unzip_code = """    mkdir -p tmp_extract
    unzip -q raw_logs.zip -d tmp_extract || { report_early_failure "Failed to extract previous logs."; exit 1; }
    
    # The structure should be raw_logs.zip containing the contents of the run directory.
    # We need to recreate the folder structure harbor expects: jobs/<run_dir>/...
    # Since the zip contains the contents of the run directory, we'll create a new folder named after the eval-id or run-id
    # Wait, the zip might contain the folder itself. Let's see how it was zipped.
    # From `save_artifacts` in entrypoint.sh: `(cd "$RUN_DIR" && zip -r "$WORK_DIR/raw_logs.zip" . -x "parsed_logs/*")`
    # This means the zip contains the *contents* of the run directory, not the folder itself.
    
    RUN_FOLDER_NAME="eval-$RESUME_FROM_RUN_ID"
    mkdir -p "$RUN_FOLDER_NAME"
    cp -a tmp_extract/. "$RUN_FOLDER_NAME/\""""

sh_content = sh_content.replace(old_unzip_code, safe_extract_code)

with open("worker/entrypoint.sh", "w") as f:
    f.write(sh_content)

print("Patched worker/entrypoint.sh")
