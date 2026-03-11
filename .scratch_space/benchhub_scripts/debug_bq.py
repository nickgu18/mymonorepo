import os
import sys
from unittest.mock import MagicMock

# Mock BigQuery Client to avoid real network calls
sys.modules['google.cloud.bigquery'] = MagicMock()

from orchestrator.main import get_bq_client, JOBS_TABLE

print(f"JOBS_TABLE: '{JOBS_TABLE}'")
bq = get_bq_client()
print(f"BQ Client: {bq}")
if bq:
    print(f"BQ Client Table: {bq.jobs_table}")
