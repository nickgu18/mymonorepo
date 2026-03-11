import sys
from unittest.mock import MagicMock

# Mock BigQuery Client
mock_bq = MagicMock()
mock_client = mock_bq.Client.return_value

sys.modules['google.cloud.bigquery'] = mock_bq

from bench_hub_common.bigquery import BigQueryClient

bq = BigQueryClient("proj", "jobs", "instances")
try:
    bq.upsert_job(
        run_id="test",
        model_name="model",
        dataset_name="ds",
        run_tags=["tag1"]
    )
    print("Called upsert_job successfully")
    args, kwargs = mock_client.query.call_args
    print("SQL Query:")
    print(args[0])
except Exception as e:
    print(f"Error calling upsert_job: {e}")
