import re

with open("projects/bench-hub/.factory/bug-490147352/worker/tests/test_bigquery_client.py", "r") as f:
    content = f.read()

old_assert = "    assert f\"UPDATE `{jobs_table}` SET status = @status\" in args[0]"
new_assert = "    assert f\"UPDATE `{jobs_table}` SET status = CASE WHEN @status = 'FINISHED'\" in args[0]"

content = content.replace(old_assert, new_assert)

with open("projects/bench-hub/.factory/bug-490147352/worker/tests/test_bigquery_client.py", "w") as f:
    f.write(content)
