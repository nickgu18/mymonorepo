with open("orchestrator/main.py", "r") as f:
    content = f.read()

old_update = """        # Update BigQuery job status to show it's running again
        bq_client.update_job_status(
            run_id=job_id,
            status=JobStatus.RUNNING,
            job_status="RUNNING",
            error_message=f"Healing {len(tasks_to_heal)} tasks via Harbor resume.",
        )"""

new_update = """        # Upsert a new row for this heal attempt to keep the history 1:MANY
        bq_client.upsert_job(
            run_id=job_id,
            job_id=heal_job_id,
            model_name=job_data.get("model_name"),
            dataset_name=job_data.get("dataset_name"),
            status=JobStatus.RUNNING,
            job_status="RUNNING",
            error_message=f"Healing {len(tasks_to_heal)} tasks via Harbor resume.",
            run_tags=job_data.get("run_tags"),
            experiment_id=job_data.get("experiment_id"),
        )"""

content = content.replace(old_update, new_update)

# Now, let's fix `BATCH_JOB_ID` environment variable.
# Wait, currently BATCH_JOB_ID is set to `job_id` (the original job's ID) so the sidecar thinks its batch job ID is the original.
# But we NEED the sidecar to know its real batch_job_id so it can update the right row!
old_env = """        new_env_vars["BATCH_JOB_ID"] = job_id"""
new_env = """        new_env_vars["BATCH_JOB_ID"] = heal_job_id"""
content = content.replace(old_env, new_env)

with open("orchestrator/main.py", "w") as f:
    f.write(content)
