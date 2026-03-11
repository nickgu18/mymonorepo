from bench_hub_common.bigquery import BigQueryClient
import json
with open("worker/config.json", "r") as f:
    config = json.load(f)
client = BigQueryClient(config["jobs_table"].split(".")[0], config["jobs_table"], config["instances_table"])
jobs = client.list_jobs(50)
for j in jobs:
    if "fb7b47aa" in j["run_id"] or "fb7b47aa" in j.get("job_id", ""):
        print(j["run_id"], j["job_id"], j["status"], j["dataset_name"])
