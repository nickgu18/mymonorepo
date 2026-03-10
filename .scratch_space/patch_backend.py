import re

with open("projects/bench-hub/.factory/bug-490147352/backend/main.py", "r") as f:
    content = f.read()

old_runs = """@app.get("/api/v1/runs")
async def list_runs(limit: int = 50):
    return await list_jobs(limit)"""

new_runs = """@app.get("/api/v1/runs")
async def list_runs(limit: int = 50, exclude_heals: bool = True):
    return await list_jobs(limit, exclude_heals)"""

old_jobs = """@app.get("/api/jobs")
async def list_jobs(limit: int = 50):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ORCHESTRATOR_URL}/api/jobs?limit={limit}", timeout=10.0
            )"""

new_jobs = """@app.get("/api/jobs")
async def list_jobs(limit: int = 50, exclude_heals: bool = True):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{ORCHESTRATOR_URL}/api/jobs?limit={limit}&exclude_heals={str(exclude_heals).lower()}", timeout=10.0
            )"""

content = content.replace(old_runs, new_runs)
content = content.replace(old_jobs, new_jobs)

with open("projects/bench-hub/.factory/bug-490147352/backend/main.py", "w") as f:
    f.write(content)
