with open("orchestrator/main.py", "r") as f:
    content = f.read()

old_term = """        # 3. Update BigQuery status
        bq_client.update_job_status(
            run_id=job_id,
            status=target_status,
            job_status=target_status.value,
            error_message=error_message,
        )"""

new_term = """        # 3. Update BigQuery status
        bq_client.update_job_status(
            run_id=job_id,
            status=target_status,
            job_status=target_status.value,
            error_message=error_message,
            job_id=job_data.get("job_id"),
        )"""

content = content.replace(old_term, new_term)

with open("orchestrator/main.py", "w") as f:
    f.write(content)
