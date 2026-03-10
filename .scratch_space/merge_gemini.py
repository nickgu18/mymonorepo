import re

with open('/usr/local/google/home/guyu/Desktop/mymonorepo/projects/harbor/src/harbor/agents/installed/gemini_cli.py', 'r') as f:
    dev_content = f.read()

with open('/usr/local/google/home/guyu/Desktop/mymonorepo/projects/harbor/upstream_gemini_cli.py', 'r') as f:
    up_content = f.read()

# We need to build the merged content. Let's just use up_content as the base, and insert dev_content parts.

# 1. Add imports
up_content = "import asyncio\nimport tarfile\nimport tempfile\nimport uuid\nimport shlex\n" + up_content
up_content = up_content.replace("from harbor.environments.docker.docker import DockerEnvironment", "")
up_content = up_content.replace("from harbor.environments.base import BaseEnvironment", "from harbor.environments.base import BaseEnvironment\nfrom harbor.environments.docker.docker import DockerEnvironment")

# 2. Add class variables
class_vars = """
    _host_setup_lock = asyncio.Lock()
    _host_setup_done = False
    _agent_commit_id: str | None = None
    _PYTHON_CANDIDATES = [
        "python3",
        "python",
        "python3.13",
        "python3.12",
        "python3.11",
        "python3.10",
    ]
"""
up_content = up_content.replace("    _image_counter: int = 0", "    _image_counter: int = 0\n" + class_vars)

# 3. Add __init__
init_block = """
    def __init__(
        self,
        logs_dir,
        prompt_template_path = None,
        version = None,
        branch = None,
        commit = None,
        tag = None,
        settings_path = None,
        credentials_path = None,
        extensions = None,
        repo_url = None,
        *args,
        **kwargs,
    ):
        super().__init__(
            logs_dir=logs_dir,
            prompt_template_path=prompt_template_path,
            version=version,
            branch=branch,
            *args,
            **kwargs,
        )
        self._commit = commit
        self._tag = tag
        self._repo_url = repo_url

        self._task_name = kwargs.get("task_name")
        self._dataset_name = kwargs.get("dataset_name")

        provided_sources = [
            p for p in [self.branch(), self._commit, self._tag] if p is not None
        ]
        if len(provided_sources) > 1:
            raise ValueError(
                "Only one of 'branch', 'commit', or 'tag' can be specified at a time."
            )

        if extensions:
            for ext in extensions:
                if not isinstance(ext, str):
                    raise ValueError(f"Extension must be a string, got {type(ext)}")
                if not re.match(r"^[a-zA-Z0-9\-_\\.\\/\\:\\@\\~]+\Z", ext):
                    raise ValueError(
                        f"Invalid extension format: '{ext}'. "
                        "Extensions must be valid URLs, GitHub paths, or npm package names "
                        "without spaces or shell metacharacters."
                    )
        self._extensions = extensions
        if settings_path:
            self._settings_path = Path(settings_path)
            if not self._settings_path.exists():
                raise FileNotFoundError(f"Settings file not found: {settings_path}")
        else:
            self._settings_path = None

        self._credentials_path = None
        if credentials_path:
            self._credentials_path = Path(credentials_path)
        elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            self._credentials_path = Path(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
        else:
            default_creds = Path.home() / ".config/gcloud/application_default_credentials.json"
            if default_creds.exists():
                self._credentials_path = default_creds
        
        if self._credentials_path and not self._credentials_path.exists():
             import warnings
             warnings.warn(f"Credentials file not found: {self._credentials_path}")
             self._credentials_path = None
        
        self._container_credentials_path = None
        self._python_interpreter = "python3"
"""
idx = up_content.find("    _PYTHON_CANDIDATES = [")
if idx != -1:
    end_idx = up_content.find("    ]", idx) + 6
    up_content = up_content[:end_idx] + "\n" + init_block + up_content[end_idx:]

# 4. Extract and inject helper methods (setup, _setup_container_git_credentials, etc.)
helpers_pattern = re.compile(r'(    async def setup\(self, environment: BaseEnvironment\) -> None:.*?)(    @staticmethod\n    def name\(\) -> str:)', re.DOTALL)
m = helpers_pattern.search(dev_content)
helpers = m.group(1) if m else ""

up_content = re.sub(r'(    @staticmethod\n    def name\(\) -> str:)', helpers + r'\1', up_content)

# 5. Extract and inject _template_variables
template_vars_pattern = re.compile(r'(    @property\n    def _template_variables\(self\) -> dict\[str, Any\]:.*?)(    def _convert_gemini_to_atif)', re.DOTALL)
m2 = template_vars_pattern.search(dev_content)
template_vars = m2.group(1) if m2 else ""

# Replace the existing _template_variables or insert if not exists
if "def _template_variables" in up_content:
    up_content = re.sub(r'(    @property\n    def _template_variables.*?)(    def)', template_vars + r'\2', up_content, flags=re.DOTALL)
else:
    up_content = re.sub(r'(    @property\n    def _install_agent_template_path\(self\) -> Path:\n        return Path\(__file__\).parent / "install-gemini-cli.sh.j2"\n)', r'\1\n' + template_vars, up_content)

# 6. Extract telemetry env vars injection from dev_content to put into create_run_agent_commands
env_injection = """
        auth_vars = [
            "GOOGLE_GENAI_USE_VERTEXAI",
            "GOOGLE_API_KEY",
        ]
        for var in auth_vars:
            if var in os.environ:
                env[var] = os.environ[var]
        
        if getattr(self, "_container_credentials_path", None):
            env["GOOGLE_APPLICATION_CREDENTIALS"] = self._container_credentials_path

        env["GEMINI_TELEMETRY_ENABLED"] = os.environ.get("GEMINI_TELEMETRY_ENABLED", "true")
        env["GEMINI_TELEMETRY_TARGET"] = os.environ.get("GEMINI_TELEMETRY_TARGET", "local")
        env["GEMINI_TELEMETRY_USE_COLLECTOR"] = os.environ.get(
            "GEMINI_TELEMETRY_USE_COLLECTOR", "false"
        )
        env["GEMINI_TELEMETRY_OUTFILE"] = os.environ.get(
            "GEMINI_TELEMETRY_OUTFILE", "/logs/agent/gemini-cli.telemetry.json"
        )
        env["USER_ID"] = os.environ.get("USER_ID", "unknown")
        env["RUN_ID"] = os.environ.get("RUN_ID", "ad-hoc")

        telemetry_vars = [
            "GEMINI_TELEMETRY_OTLP_ENDPOINT",
            "GEMINI_TELEMETRY_OTLP_PROTOCOL",
            "GEMINI_TELEMETRY_LOG_PROMPTS",
            "GEMINI_TELEMETRY_USE_CLI_AUTH",
            "OTLP_GOOGLE_CLOUD_PROJECT",
        ]
        for var in telemetry_vars:
            if var in os.environ:
                env[var] = os.environ[var]

        is_gcp = env["GEMINI_TELEMETRY_TARGET"] == "gcp"
        python_interp = getattr(self, "_python_interpreter", None)
        has_python = python_interp is not None
        is_collector = (
            env["GEMINI_TELEMETRY_USE_COLLECTOR"].lower() in ("true", "1") and has_python
        )

        if env["GEMINI_TELEMETRY_USE_COLLECTOR"].lower() in ("true", "1") and not has_python:
            self.logger.warning(
                "Telemetry collector requested but no python interpreter was found. "
                "Falling back to local file telemetry."
            )
            env["GEMINI_TELEMETRY_TARGET"] = "local"
            is_gcp = False

        if is_collector:
            env["GEMINI_TELEMETRY_OTLP_ENDPOINT"] = "http://localhost:4318"
            env["GEMINI_TELEMETRY_OTLP_PROTOCOL"] = "http"
            env["GEMINI_TELEMETRY_TARGET"] = "local"

        if is_gcp or is_collector:
            env.pop("GEMINI_TELEMETRY_OUTFILE", None)

        telemetry_exports = []
        for k, v in env.items():
            if k.startswith("GEMINI_TELEMETRY_"):
                telemetry_exports.append(f"export {k}='{v}'")
        
        export_cmd = " && ".join(telemetry_exports) + " && " if telemetry_exports else ""
"""

# Add env_injection before commands: list[ExecInput] = [] in create_run_agent_commands
up_content = up_content.replace("        commands: list[ExecInput] = []", env_injection + "\n        commands: list[ExecInput] = []")

# Modify the command appending in create_run_agent_commands to add the run_id, model, etc.
cmd_mod = """
        if getattr(self, "_dataset_name", None) and getattr(self, "_task_name", None):
            cmd += f" --run-id {shlex.quote(self._dataset_name)}/{shlex.quote(self._task_name)}"

        cmd = export_cmd + cmd

        commands.append("""
up_content = up_content.replace("        commands.append(", cmd_mod)


# 7. Add create_cleanup_commands Telemetry override
cleanup_override = """    def create_cleanup_commands(self) -> list[ExecInput]:
        copy_command = (
            "find ~/.gemini/tmp -type f -name 'session-*.json' 2>/dev/null | "
            "head -n 1 | xargs -r -I{} cp {} /logs/agent/gemini-cli.trajectory.json"
        )
        copy_telemetry_command = (
            "find ~/.gemini/tmp -type f -name 'telemetry-*.json' 2>/dev/null | "
            "head -n 1 | xargs -r -I{} cp {} /logs/agent/gemini-cli.telemetry.json"
        )

        if str(self.logs_dir) != "/logs/agent":
             copy_telemetry_command += (
                 f" || cp {self.logs_dir}/gemini-cli.telemetry.json /logs/agent/gemini-cli.telemetry.json 2>/dev/null"
             )
        return [
            ExecInput(
                command=f"{copy_command} ; {copy_telemetry_command}",
            ),
        ]
"""
up_content = re.sub(r'    def create_cleanup_commands.*?\]\n', cleanup_override, up_content, flags=re.DOTALL)

with open('/usr/local/google/home/guyu/Desktop/mymonorepo/projects/harbor/src/harbor/agents/installed/gemini_cli.py', 'w') as f:
    f.write(up_content)

