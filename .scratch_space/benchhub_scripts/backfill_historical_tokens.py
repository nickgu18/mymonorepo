import os
import json
import logging
import io
import zipfile
from datetime import datetime, timezone
from google.cloud import bigquery, storage

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = "ai-incubation-team"
GCS_BUCKET = "my-harbor-results-bucket"
DATASET_ID = "evals"
JOBS_TABLE = f"{PROJECT_ID}.{DATASET_ID}.eval_results_jobs"
INSTANCES_TABLE = f"{PROJECT_ID}.{DATASET_ID}.eval_results_instances"

def extract_from_content(content):
    """
    Extracts token counts from telemetry content.
    Handles single JSON objects, JSONL, and concatenated JSON.
    """
    total_input = 0
    total_output = 0
    total_cached = 0
    total_thoughts = 0

    def process_node(item):
        nonlocal total_input, total_output, total_cached, total_thoughts
        if not isinstance(item, dict):
            return
        
        # Check attributes for the api_response event
        attrs = item.get("attributes", {})
        if isinstance(attrs, dict) and attrs.get("event.name") == "gemini_cli.api_response":
            total_input += int(attrs.get("input_token_count") or 0)
            total_output += int(attrs.get("output_token_count") or 0)
            total_cached += int(attrs.get("cached_content_token_count") or 0)
            total_thoughts += int(attrs.get("thoughts_token_count") or 0)
        
        # Recurse into children only if necessary
        for key in ["resourceSpans", "scopeSpans", "spans", "events"]:
            if key in item and isinstance(item[key], list):
                for child in item[key]:
                    process_node(child)

    # 1. Try parsing as a single JSON object
    try:
        data = json.loads(content)
        process_node(data)
        return total_input, total_output, total_cached, total_thoughts
    except json.JSONDecodeError:
        pass

    # 2. Try parsing as concatenated JSON using raw_decode
    decoder = json.JSONDecoder()
    pos = 0
    while pos < len(content):
        # Skip whitespace
        while pos < len(content) and content[pos].isspace():
            pos += 1
        if pos >= len(content):
            break
            
        try:
            obj, pos = decoder.raw_decode(content, pos)
            process_node(obj)
        except json.JSONDecodeError:
            # Skip to next potential object
            pos = content.find('{', pos + 1)
            if pos == -1: break
        except Exception as e:
            logger.error(f"Unexpected error during decoding: {e}")
            break
            
    return total_input, total_output, total_cached, total_thoughts

def backfill(target_run_id=None, limit=None, dry_run=False, since=None):
    client = bigquery.Client(project=PROJECT_ID)
    storage_client = storage.Client(project=PROJECT_ID)
    
    if dry_run:
        logger.info("DRY RUN: No BigQuery updates will be performed.")

    # 1. Find jobs that need backfilling using parameterized query
    query_params = []
    
    if target_run_id:
        # Relax where clause for specific run_id to allow testing/re-processing
        where_clause = "run_id = @run_id"
        query_params.append(bigquery.ScalarQueryParameter("run_id", "STRING", target_run_id))
    else:
        # Default criteria: jobs with 0 tokens but with successes
        where_clause = "(total_input_tokens = 0 OR total_input_tokens IS NULL) AND passed_instances > 0"
        if since:
            where_clause += " AND created_at >= @since"
            query_params.append(bigquery.ScalarQueryParameter("since", "TIMESTAMP", since))
    
    limit_clause = f"LIMIT {limit}" if limit else ""
    
    query = f"""
        SELECT run_id, dataset_name, model_name 
        FROM `{JOBS_TABLE}` 
        WHERE {where_clause}
        ORDER BY created_at DESC
        {limit_clause}
    """
    
    job_config = bigquery.QueryJobConfig(query_parameters=query_params)
    logger.info(f"Querying BigQuery for jobs to backfill...")
    jobs_to_fix = list(client.query(query, job_config=job_config).result())
    logger.info(f"Found {len(jobs_to_fix)} jobs to process.")

    for job in jobs_to_fix:
        run_id = job.run_id
        logger.info(f">>> Starting backfill for {run_id}...")
        
        # Initialize job counters and aggregation dictionary
        total_job_input = 0
        total_job_output = 0
        total_job_cached = 0
        total_job_thoughts = 0
        instance_map = {} # instance_id -> {counts}

        bucket = storage_client.bucket(GCS_BUCKET, user_project=PROJECT_ID)
        zip_blob = bucket.blob(f"{run_id}/raw_logs.zip")
        
        if not zip_blob.exists():
            logger.warning(f"No raw_logs.zip found for {run_id}. Skipping.")
            continue

        zip_blob.reload()
        logger.info(f"Downloading raw_logs.zip ({zip_blob.size / 1024 / 1024:.1f} MB)...")
        zip_content = zip_blob.download_as_bytes()
        
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            telemetry_files = [f for f in z.namelist() if f.endswith('gemini-cli.telemetry.json')]
            logger.info(f"Found {len(telemetry_files)} telemetry files. Processing...")
            
            for i, t_file in enumerate(telemetry_files):
                try:
                    path_parts = t_file.split("/")
                    dir_name = path_parts[0]
                    instance_id = "__".join(dir_name.split("__")[:-1]) if "__" in dir_name else dir_name
                    
                    with z.open(t_file) as f:
                        content = f.read().decode('utf-8')
                        i_in, i_out, i_ca, i_th = extract_from_content(content)
                        
                        if i_in > 0:
                            if instance_id not in instance_map:
                                instance_map[instance_id] = {
                                    "input_tokens": 0,
                                    "output_tokens": 0,
                                    "cached_tokens": 0,
                                    "thoughts_tokens": 0
                                }
                            
                            instance_map[instance_id]["input_tokens"] += i_in
                            instance_map[instance_id]["output_tokens"] += i_out
                            instance_map[instance_id]["cached_tokens"] += i_ca
                            instance_map[instance_id]["thoughts_tokens"] += i_th
                            
                            total_job_input += i_in
                            total_job_output += i_out
                            total_job_cached += i_ca
                            total_job_thoughts += i_th
                    
                    if (i + 1) % 50 == 0:
                        logger.info(f"  Processed {i+1}/{len(telemetry_files)} instances...")
                except Exception as e:
                    logger.warning(f"Error processing {t_file}: {e}")

        # Convert map to list for batch updates
        instance_updates = [
            {
                "run_id": run_id,
                "instance_id": i_id,
                **counts
            }
            for i_id, counts in instance_map.items()
        ]

        if total_job_input > 0:
            if dry_run:
                logger.info(f"DRY RUN: Would update {len(instance_updates)} instances and job summary for {run_id}")
                logger.info(f"DRY RUN: Totals - Input: {total_job_input}, Output: {total_job_output}, Cached: {total_job_cached}, Thoughts: {total_job_thoughts}")
                continue

            logger.info(f"Updating {len(instance_updates)} instances in BigQuery...")
            # Batch update instances using MERGE with an Array of Structs
            for j in range(0, len(instance_updates), 50):
                chunk = instance_updates[j:j+50]
                
                merge_query = f"""
                    MERGE `{INSTANCES_TABLE}` T
                    USING UNNEST(@updates) S
                    ON T.run_id = S.run_id AND T.instance_id = S.instance_id
                    WHEN MATCHED THEN
                        UPDATE SET 
                            input_tokens = S.input_tokens,
                            output_tokens = S.output_tokens,
                            cached_tokens = S.cached_tokens,
                            thoughts_tokens = S.thoughts_tokens
                """
                
                # Correct way to pass a list of STRUCTs:
                # ArrayQueryParameter with values being list of ScalarQueryParameter for each struct field
                # but actually, easier is just a list of ScalarQueryParameters or specialized StructQueryParameter if it existed.
                # In google-cloud-bigquery, for STRUCT, you pass a list of ScalarQueryParameter objects.
                
                params = [
                    bigquery.ArrayQueryParameter(
                        "updates", 
                        "STRUCT",
                        [
                            bigquery.StructQueryParameter(
                                "unused_name", # BigQuery doesn't use this name inside UNNEST usually but the API requires it
                                bigquery.ScalarQueryParameter("run_id", "STRING", u["run_id"]),
                                bigquery.ScalarQueryParameter("instance_id", "STRING", u["instance_id"]),
                                bigquery.ScalarQueryParameter("input_tokens", "INTEGER", u["input_tokens"]),
                                bigquery.ScalarQueryParameter("output_tokens", "INTEGER", u["output_tokens"]),
                                bigquery.ScalarQueryParameter("cached_tokens", "INTEGER", u["cached_tokens"]),
                                bigquery.ScalarQueryParameter("thoughts_tokens", "INTEGER", u["thoughts_tokens"]),
                            ) for u in chunk
                        ]
                    )
                ]
                
                job_config = bigquery.QueryJobConfig(query_parameters=params)
                client.query(merge_query, job_config=job_config).result()
                logger.info(f"  Batch {j//50 + 1} complete.")

            logger.info(f"Updating job summary for {run_id}...")
            update_job_sql = f"""
                UPDATE `{JOBS_TABLE}`
                SET total_input_tokens = @input,
                    total_output_tokens = @output,
                    total_cached_tokens = @cached,
                    total_thoughts_tokens = @thoughts,
                    updated_at = CURRENT_TIMESTAMP()
                WHERE run_id = @run_id
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("input", "INTEGER", total_job_input),
                    bigquery.ScalarQueryParameter("output", "INTEGER", total_job_output),
                    bigquery.ScalarQueryParameter("cached", "INTEGER", total_job_cached),
                    bigquery.ScalarQueryParameter("thoughts", "INTEGER", total_job_thoughts),
                    bigquery.ScalarQueryParameter("run_id", "STRING", run_id),
                ]
            )
            client.query(update_job_sql, job_config=job_config).result()
            logger.info(f"SUCCESS: Fully updated {run_id} (Input: {total_job_input}, Output: {total_job_output})")
        else:
            logger.warning(f"No tokens recovered for {run_id}.")
            
    logger.info("Backfill process finished.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Backfill missing token data from GCS raw_logs.zip")
    parser.add_argument("--run_id", help="Process only this specific run_id")
    parser.add_argument("--limit", type=int, help="Limit the number of jobs to process")
    parser.add_argument("--dry_run", action="store_true", help="Do not perform BigQuery updates")
    parser.add_argument("--since", help="Process only jobs created at or after this date (YYYY-MM-DD)")
    args = parser.parse_args()
    
    backfill(target_run_id=args.run_id, limit=args.limit, dry_run=args.dry_run, since=args.since)
