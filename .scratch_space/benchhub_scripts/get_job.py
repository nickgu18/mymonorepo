from bench_hub_common.bigquery import BigQueryClient
import json
with open("worker/config.json", "r") as f:
    config = json.load(f)
client = BigQueryClient(config["jobs_table"].split(".")[0], config["jobs_table"], config["instances_table"])
print(client.get_job("fb7b47aa"))
