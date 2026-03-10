import re

file_path = "/usr/local/google/home/guyu/Desktop/mymonorepo/projects/harbor/src/harbor/agents/installed/base.py"
with open(file_path, "r") as f:
    content = f.read()

# Replace block 1
block1 = """<<<<<<< HEAD
        branch: str | None = None,
=======
        extra_env: dict[str, str] | None = None,
>>>>>>> upstream/main"""
replacement1 = """        branch: str | None = None,
        extra_env: dict[str, str] | None = None,"""
content = content.replace(block1, replacement1)

# Replace block 2
block2 = """<<<<<<< HEAD
    def branch(self) -> str | None:
        return self._branch
=======
    def get_version_command(self) -> str | None:
        \"\"\"Return a shell command that prints the agent version to stdout.
        Override in subclasses to enable auto-detection after setup.\"\"\"
        return None

    def parse_version(self, stdout: str) -> str:
        \"\"\"Parse the output of get_version_command into a version string.
        Override in subclasses if the command output needs parsing.\"\"\"
        return stdout.strip()

    def _setup_env(self) -> dict[str, str]:
        \"\"\"Environment variables for install script execution.\"\"\"
        return {"DEBIAN_FRONTEND": "noninteractive"}

    def _truncate_output(self, text: str | None, max_len: int = 1000) -> str:
        if not text:
            return "None"
        if len(text) > max_len:
            return text[:max_len] + " ... [truncated]"
        return text
>>>>>>> upstream/main"""
replacement2 = """    def branch(self) -> str | None:
        return self._branch

    def get_version_command(self) -> str | None:
        \"\"\"Return a shell command that prints the agent version to stdout.
        Override in subclasses to enable auto-detection after setup.\"\"\"
        return None

    def parse_version(self, stdout: str) -> str:
        \"\"\"Parse the output of get_version_command into a version string.
        Override in subclasses if the command output needs parsing.\"\"\"
        return stdout.strip()

    def _setup_env(self) -> dict[str, str]:
        \"\"\"Environment variables for install script execution.\"\"\"
        return {"DEBIAN_FRONTEND": "noninteractive"}

    def _truncate_output(self, text: str | None, max_len: int = 1000) -> str:
        if not text:
            return "None"
        if len(text) > max_len:
            return text[:max_len] + " ... [truncated]"
        return text"""
content = content.replace(block2, replacement2)

# Replace block 3
block3 = """<<<<<<< HEAD
        self.populate_context_post_run(context)
=======
                if result.stderr:
                    (command_dir / "stderr.txt").write_text(result.stderr)

                if result.return_code != 0:
                    truncated_stdout = self._truncate_output(result.stdout)
                    truncated_stderr = self._truncate_output(result.stderr)
                    raise NonZeroAgentExitCodeError(
                        f"Agent command failed (exit code {result.return_code})\\n"
                        f"Command: {exec_input.command}\\n"
                        f"Stdout:\\n{truncated_stdout}\\n"
                        f"Stderr:\\n{truncated_stderr}\\n"
                    )
        finally:
            for cleanup_input in self.create_cleanup_commands():
                try:
                    await environment.exec(
                        command=cleanup_input.command,
                        cwd=cleanup_input.cwd,
                        env=cleanup_input.env,
                        timeout_sec=cleanup_input.timeout_sec,
                    )
                except Exception as e:
                    print(f"Cleanup command failed: {e}")

            self.populate_context_post_run(context)
>>>>>>> upstream/main"""
replacement3 = """                if result.stderr:
                    (command_dir / "stderr.txt").write_text(result.stderr)

                if result.return_code != 0:
                    truncated_stdout = self._truncate_output(result.stdout)
                    truncated_stderr = self._truncate_output(result.stderr)
                    raise NonZeroAgentExitCodeError(
                        f"Agent command failed (exit code {result.return_code})\\n"
                        f"Command: {exec_input.command}\\n"
                        f"Stdout:\\n{truncated_stdout}\\n"
                        f"Stderr:\\n{truncated_stderr}\\n"
                    )
        finally:
            for cleanup_input in self.create_cleanup_commands():
                try:
                    await environment.exec(
                        command=cleanup_input.command,
                        cwd=cleanup_input.cwd,
                        env=cleanup_input.env,
                        timeout_sec=cleanup_input.timeout_sec,
                    )
                except Exception as e:
                    print(f"Cleanup command failed: {e}")

            self.populate_context_post_run(context)"""
content = content.replace(block3, replacement3)

with open(file_path, "w") as f:
    f.write(content)
