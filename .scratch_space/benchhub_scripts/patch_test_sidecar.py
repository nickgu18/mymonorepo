import re

with open("worker/tests/test_sidecar_monitor.py", "r") as f:
    content = f.read()

content = re.sub(
    r'error_message="Fatal Harbor Error: Git clone failed",\n\s*\)',
    'error_message="Fatal Harbor Error: Git clone failed",\n                job_id="some-value",\n            )',
    content,
)

with open("worker/tests/test_sidecar_monitor.py", "w") as f:
    f.write(content)
