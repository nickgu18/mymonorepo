import re

with open("projects/bench-hub/.factory/bug-490147352/web-ui/src/components/RunSummary.tsx", "r") as f:
    content = f.read()

old_logic = "  const canHeal = details.status === 'FAILED' || details.status === 'CANCELLED' || details.error_instances > 0 || (details.status !== 'RUNNING' && details.status !== 'PENDING' && details.status !== 'QUEUED' && details.completed_instances < details.total_instances);"
new_logic = "  const canHeal = details.status === 'BROKEN';"

content = content.replace(old_logic, new_logic)

with open("projects/bench-hub/.factory/bug-490147352/web-ui/src/components/RunSummary.tsx", "w") as f:
    f.write(content)
