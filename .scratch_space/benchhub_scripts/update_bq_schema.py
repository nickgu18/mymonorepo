import os
from google.cloud import bigquery

# Default to production values
PROJECT_ID = os.getenv("PROJECT_ID", "ai-incubation-team")
DATASET_ID = os.getenv("DATASET_ID", "evals")
JOBS_TABLE = os.getenv("JOBS_TABLE", "eval_results_jobs")
INSTANCES_TABLE = os.getenv("INSTANCES_TABLE", "eval_results_instances")

def update_schema():
    client = bigquery.Client(project=PROJECT_ID)
    
    # 1. Update Jobs Table
    jobs_full_id = f"{PROJECT_ID}.{DATASET_ID}.{JOBS_TABLE}"
    print(f"Updating table {jobs_full_id}...")
    queries = [
        f"ALTER TABLE `{jobs_full_id}` ADD COLUMN IF NOT EXISTS total_cost FLOAT64",
        f"ALTER TABLE `{jobs_full_id}` ADD COLUMN IF NOT EXISTS total_input_tokens INTEGER",
        f"ALTER TABLE `{jobs_full_id}` ADD COLUMN IF NOT EXISTS total_output_tokens INTEGER",
        f"ALTER TABLE `{jobs_full_id}` ADD COLUMN IF NOT EXISTS total_cached_tokens INTEGER",
        f"ALTER TABLE `{jobs_full_id}` ADD COLUMN IF NOT EXISTS total_thoughts_tokens INTEGER",
        f"ALTER TABLE `{jobs_full_id}` ADD COLUMN IF NOT EXISTS experiment_id STRING",
        f"ALTER TABLE `{jobs_full_id}` ADD COLUMN IF NOT EXISTS arm_name STRING",
    ]
    
    for query in queries:
        try:
            client.query(query).result()
            print(f"Executed: {query}")
        except Exception as e:
            print(f"Error executing {query}: {e}")

    # 2. Update Instances Table
    instances_full_id = f"{PROJECT_ID}.{DATASET_ID}.{INSTANCES_TABLE}"
    print(f"Updating table {instances_full_id}...")
    queries = [
        f"ALTER TABLE `{instances_full_id}` ADD COLUMN IF NOT EXISTS cost FLOAT64",
        f"ALTER TABLE `{instances_full_id}` ADD COLUMN IF NOT EXISTS input_tokens INTEGER",
        f"ALTER TABLE `{instances_full_id}` ADD COLUMN IF NOT EXISTS output_tokens INTEGER",
        f"ALTER TABLE `{instances_full_id}` ADD COLUMN IF NOT EXISTS cached_tokens INTEGER",
        f"ALTER TABLE `{instances_full_id}` ADD COLUMN IF NOT EXISTS thoughts_tokens INTEGER",
    ]
    
    for query in queries:
        try:
            client.query(query).result()
            print(f"Executed: {query}")
        except Exception as e:
            print(f"Error executing {query}: {e}")

if __name__ == "__main__":
    update_schema()
