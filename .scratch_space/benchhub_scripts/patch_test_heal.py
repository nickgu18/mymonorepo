with open("orchestrator/tests/test_heal.py", "r") as f:
    content = f.read()

old_assert = """    # Verify bq updated
    mock_bq_client.update_job_status.assert_called_once()
    kwargs = mock_bq_client.update_job_status.call_args[1]
    assert kwargs["run_id"] == "job-123"
    assert kwargs["status"] == JobStatus.RUNNING"""

new_assert = """    # Verify bq updated via upsert_job
    mock_bq_client.upsert_job.assert_called_once()
    kwargs = mock_bq_client.upsert_job.call_args[1]
    assert kwargs["run_id"] == "job-123"
    assert kwargs["status"] == JobStatus.RUNNING
    assert "heal-" in kwargs["job_id"]"""

content = content.replace(old_assert, new_assert)

with open("orchestrator/tests/test_heal.py", "w") as f:
    f.write(content)
