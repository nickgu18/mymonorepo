import os
from bench_hub_common.bigquery import BigQueryClient

PROJECT_ID = "ai-incubation-team"
JOBS_TABLE = "ai-incubation-team.evals.eval_results_jobs"
INSTANCES_TABLE = "ai-incubation-team.evals.eval_results_instances"

bq = BigQueryClient(PROJECT_ID, JOBS_TABLE, INSTANCES_TABLE)
run_id = "benchhub-eval-68275684"

print(f"Fetching instances for run: {run_id}")
instances = bq.list_instances(run_id)
print(f"Found {len(instances)} instances")

if instances:
    print("First instance sample:")
    print(instances[0])
else:
    print("No instances found via client.")
