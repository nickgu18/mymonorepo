with open("worker/entrypoint.sh", "r") as f:
    content = f.read()

import re

# Need to replace the inline python3 blocks.
old_block1 = """    RUN_FOLDER_NAME=$(python3 -c '
import zipfile
import os
import json
import sys
zip_path = "raw_logs.zip"
run_folder_name = "eval-" + os.environ.get("RESUME_FROM_RUN_ID", "unknown")
try:
    with zipfile.ZipFile(zip_path, "r") as zf:
        if "config.json" in zf.namelist():
            with zf.open("config.json") as f:
                config = json.load(f)
                if "run_id" in config:
                    run_folder_name = config["run_id"]
                elif "eval_id" in config:
                    run_folder_name = config["eval_id"]
except Exception as e:
    print(f"Failed to read config.json from zip: {e}", file=sys.stderr)

print(run_folder_name)
')"""

new_block1 = """    RUN_FOLDER_NAME=$(python3 /app/scripts/get_run_folder.py)"""

content = content.replace(old_block1, new_block1)

old_block2 = """    # Safe extraction to prevent Zip Slip
    python3 -c '
import zipfile
import os
import sys
extract_dir = os.path.abspath(sys.argv[1])
zip_path = "raw_logs.zip"
try:
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.namelist():
            member_path = os.path.abspath(os.path.join(extract_dir, member))
            if member_path.startswith(extract_dir + os.sep) or member_path == extract_dir:
                zf.extract(member, extract_dir)
except Exception as e:
    print(f"Extraction failed: {e}", file=sys.stderr)
    sys.exit(1)
' "$RUN_FOLDER_NAME" || { report_early_failure "Failed to safely extract previous logs."; exit 1; }"""

new_block2 = """    # Safe extraction to prevent Zip Slip
    python3 /app/scripts/safe_extract.py "$RUN_FOLDER_NAME" || { report_early_failure "Failed to safely extract previous logs."; exit 1; }"""

content = content.replace(old_block2, new_block2)

with open("worker/entrypoint.sh", "w") as f:
    f.write(content)
