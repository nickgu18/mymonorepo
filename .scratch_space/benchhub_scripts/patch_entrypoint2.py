with open("worker/entrypoint.sh", "r") as f:
    content = f.read()

# Try with re
import re

content = re.sub(r"    RUN_FOLDER_NAME=\$\(python3 -c '.*?print\(run_folder_name\)\n'\)", "    RUN_FOLDER_NAME=$(python3 /app/scripts/get_run_folder.py)", content, flags=re.DOTALL)

content = re.sub(r"    # Safe extraction to prevent Zip Slip\n    python3 -c '.*?\n' \"\$RUN_FOLDER_NAME\" \|\| \{ report_early_failure \"Failed to safely extract previous logs\.\"; exit 1; \}", "    # Safe extraction to prevent Zip Slip\n    python3 /app/scripts/safe_extract.py \"$RUN_FOLDER_NAME\" || { report_early_failure \"Failed to safely extract previous logs.\"; exit 1; }", content, flags=re.DOTALL)

with open("worker/entrypoint.sh", "w") as f:
    f.write(content)
