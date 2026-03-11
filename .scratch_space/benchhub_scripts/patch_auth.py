with open("orchestrator/main.py", "r") as f:
    content = f.read()

old_auth = """        elif os.environ.get("K_SERVICE"):  # Prod environment should have this header
            logger.warning(
                f"Missing X-Goog-Authenticated-User-Email for heal_job on {job_id}"
            )"""

new_auth = """        elif os.environ.get("K_SERVICE"):  # Prod environment should have this header
            logger.warning(
                f"Missing X-Goog-Authenticated-User-Email for heal_job on {job_id}"
            )
            raise HTTPException(
                status_code=401, detail="Authentication required"
            )"""

content = content.replace(old_auth, new_auth)

with open("orchestrator/main.py", "w") as f:
    f.write(content)
