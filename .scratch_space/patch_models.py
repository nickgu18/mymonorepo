import re

with open("projects/bench-hub/.factory/bug-490147352/common/src/bench_hub_common/models.py", "r") as f:
    content = f.read()

old_status = """    UNKNOWN = "UNKNOWN"
    FINISHED = "FINISHED\""""

new_status = """    UNKNOWN = "UNKNOWN"
    FINISHED = "FINISHED"
    BROKEN = "BROKEN\""""

content = content.replace(old_status, new_status)

with open("projects/bench-hub/.factory/bug-490147352/common/src/bench_hub_common/models.py", "w") as f:
    f.write(content)
