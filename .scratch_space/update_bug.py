import requests
import json
import subprocess

COMMENT = """I have reviewed the upstream updates and merged `main` into our `dev-main` branch at https://github.com/googlecloud-appeco-incubator/harbor/pull/6

**Key Features Added:**
- Multi-modal trajectory support (image handling for tool calls).
- Improved robust cleanup commands mechanism for agent executions.
- Env Var and CLI Flag property extensions on the base agent class.

**Impact on our Existing Workflow (especially bench-hub):**
- Fixes issues with `return_code` handling which makes our docker orchestrator execution loop more resilient.
- Multi-modal support unlocks evaluation capabilities for vision tasks within bench-hub.
- bench-hub telemetry is fully preserved through the `create_cleanup_commands` overrides."""

script = f"""
cat << 'INNER_EOF' > /tmp/bug_comment.txt
{COMMENT}
INNER_EOF
"""
with open("/tmp/update_bug.sh", "w") as f:
    f.write(script)
