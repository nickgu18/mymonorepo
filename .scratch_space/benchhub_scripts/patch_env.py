with open("orchestrator/main.py", "r") as f:
    content = f.read()

# Instead of relying on `old_env.secret_variables` which might be scrubbed by the GCP API upon read, we'll explicitly inject the known secret variables just like in `submit_job`.

old_env_code = """        new_job.task_groups[0].task_spec.environment = batch_v1.Environment(
            variables=new_env_vars, secret_variables=dict(old_env.secret_variables)
        )"""

new_env_code = """        # Re-inject secret_variables explicitly, as they might be scrubbed when reading from the API
        secret_vars = dict(old_env.secret_variables)
        if "GITHUB_TOKEN" not in secret_vars:
            # Fallback to the default secret path if the API stripped it out
            secret_vars["GITHUB_TOKEN"] = "projects/329116254836/secrets/HARBOR_GITHUB_TOKEN/versions/latest"

        new_job.task_groups[0].task_spec.environment = batch_v1.Environment(
            variables=new_env_vars, secret_variables=secret_vars
        )"""

content = content.replace(old_env_code, new_env_code)

with open("orchestrator/main.py", "w") as f:
    f.write(content)
