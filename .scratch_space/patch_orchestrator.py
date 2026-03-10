import re

with open("projects/bench-hub/.factory/bug-490147352/orchestrator/main.py", "r") as f:
    content = f.read()

old_func = """@app.get("/api/jobs", response_model=JobListResponse)
@app.get("/jobs", response_model=JobListResponse)
async def list_jobs(limit: int = 50):
    try:
        bq_client = get_bq_client()
        if not bq_client:
            return JobListResponse(jobs=[])

        jobs_data = bq_client.list_jobs(limit=limit)"""

new_func = """@app.get("/api/jobs", response_model=JobListResponse)
@app.get("/jobs", response_model=JobListResponse)
async def list_jobs(limit: int = 50, exclude_heals: bool = True):
    try:
        bq_client = get_bq_client()
        if not bq_client:
            return JobListResponse(jobs=[])

        jobs_data = bq_client.list_jobs(limit=limit, exclude_heals=exclude_heals)"""

content = content.replace(old_func, new_func)

with open("projects/bench-hub/.factory/bug-490147352/orchestrator/main.py", "w") as f:
    f.write(content)
