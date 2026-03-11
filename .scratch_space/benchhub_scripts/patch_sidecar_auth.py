with open("worker/sidecar_monitor.py", "r") as f:
    content = f.read()

# Current logic skips initial registration if run_id exists, which breaks the 1:MANY logic! We WANT to insert a new row if the job_id doesn't match!

old_skip = """            existing_job = bq_client.get_job(run_id)
            if existing_job:
                logger.info(
                    f"Found existing job {run_id} in BigQuery. Skipping initial registration."
                )
            else:"""

new_skip = """            existing_job = bq_client.get_job(run_id)
            # Only skip if the exact job_id is already registered for this run_id
            if existing_job and existing_job.get("job_id") == batch_job_id:
                logger.info(
                    f"Found existing job {run_id} (batch {batch_job_id}) in BigQuery. Skipping initial registration."
                )
            else:"""

content = content.replace(old_skip, new_skip)

with open("worker/sidecar_monitor.py", "w") as f:
    f.write(content)

