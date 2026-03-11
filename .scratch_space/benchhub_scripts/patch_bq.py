with open("common/src/bench_hub_common/bigquery.py", "r") as f:
    content = f.read()

old_join = """                FROM new_data n
                LEFT JOIN `{jobs_table}` e ON n.run_id = e.run_id"""

# Fix: We want to join only with the *most recent* row for that run_id to grab its tags.
# If we join directly on jobs_table, we get all attempts. 
# We should use a subquery with ROW_NUMBER() OVER(PARTITION BY run_id ORDER BY updated_at DESC) as rn where rn=1.
new_join = """                FROM new_data n
                LEFT JOIN (
                    SELECT * FROM (
                        SELECT *, ROW_NUMBER() OVER(PARTITION BY run_id ORDER BY updated_at DESC) as rn
                        FROM `{jobs_table}`
                    ) WHERE rn = 1
                ) e ON n.run_id = e.run_id"""

content = content.replace(old_join, new_join)

with open("common/src/bench_hub_common/bigquery.py", "w") as f:
    f.write(content)
