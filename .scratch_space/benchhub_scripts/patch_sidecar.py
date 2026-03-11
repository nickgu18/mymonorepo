with open("worker/sidecar_monitor.py", "r") as f:
    content = f.read()

old_call = """        bq_client.update_job_status(
            run_id,
            status,
            artifacts_url=artifacts_url,
            job_status=final_job_status,
            error_message=error_message,
        )"""

new_call = """        bq_client.update_job_status(
            run_id,
            status,
            artifacts_url=artifacts_url,
            job_status=final_job_status,
            error_message=error_message,
            job_id=batch_job_id,
        )"""

content = content.replace(old_call, new_call)

with open("worker/sidecar_monitor.py", "w") as f:
    f.write(content)
