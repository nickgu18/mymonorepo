import re

with open("projects/bench-hub/.factory/bug-490147352/common/src/bench_hub_common/bigquery.py", "r") as f:
    content = f.read()

old_func = """        status_val = getattr(status, "value", status)

        set_clause = "status = @status, updated_at = @now\""""

new_func = """        status_val = getattr(status, "value", status)

        set_clause = "status = CASE WHEN @status = 'FINISHED' AND (COALESCE(error_instances, 0) > 0 OR COALESCE(failed_instances, 0) > 0) THEN 'BROKEN' ELSE @status END, updated_at = @now\""""

content = content.replace(old_func, new_func)

with open("projects/bench-hub/.factory/bug-490147352/common/src/bench_hub_common/bigquery.py", "w") as f:
    f.write(content)
