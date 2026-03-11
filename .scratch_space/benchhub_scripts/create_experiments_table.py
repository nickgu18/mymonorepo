from google.cloud import bigquery
import os

PROJECT_ID = "ai-incubation-team"
DATASET_ID = "evals"
TABLE_ID = "experiments"

def create_table():
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("creator", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("control_arm_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("experiment_arm_ids", "STRING", mode="REPEATED"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    ]
    
    table = bigquery.Table(table_ref, schema=schema)
    
    try:
        table = client.create_table(table)
        print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"Table {table_ref} already exists.")
        else:
            print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_table()
