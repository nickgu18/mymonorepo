import re

with open("projects/bench-hub/.factory/bug-490147352/common/src/bench_hub_common/bigquery.py", "r") as f:
    content = f.read()

old_func = """    def list_jobs(self, limit: int = 50) -> list[dict]:
        \"\"\"
        Lists all jobs from the jobs table, ordered by created_at DESC.

        Args:
            limit: Maximum number of jobs to return.

        Returns:
            A list of dictionaries containing job details.
        \"\"\"
        jobs_table = self.jobs_table
        query = f"SELECT * FROM `{jobs_table}` ORDER BY created_at DESC LIMIT @limit"
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("limit", "INTEGER", limit),
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        return [dict(row) for row in query_job.result()]"""

new_func = """    def list_jobs(self, limit: int = 50, exclude_heals: bool = True) -> list[dict]:
        \"\"\"
        Lists all jobs from the jobs table, ordered by created_at DESC.

        Args:
            limit: Maximum number of jobs to return.
            exclude_heals: If True, exclude jobs with ID containing '-heal-' or having a 'heal_of=' tag.

        Returns:
            A list of dictionaries containing job details.
        \"\"\"
        jobs_table = self.jobs_table
        
        where_clause = ""
        if exclude_heals:
            where_clause = "WHERE run_id NOT LIKE '%-heal-%' AND NOT EXISTS (SELECT 1 FROM UNNEST(run_tags) AS tag WHERE tag LIKE 'heal_of=%')"
            
        query = f"SELECT * FROM `{jobs_table}` {where_clause} ORDER BY created_at DESC LIMIT @limit"
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("limit", "INTEGER", limit),
            ]
        )
        query_job = self.client.query(query, job_config=job_config)
        return [dict(row) for row in query_job.result()]"""

content = content.replace(old_func, new_func)

with open("projects/bench-hub/.factory/bug-490147352/common/src/bench_hub_common/bigquery.py", "w") as f:
    f.write(content)
