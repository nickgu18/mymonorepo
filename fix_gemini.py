import re

with open('src/harbor/agents/installed/gemini_cli.py', 'r') as f:
    text = f.read()

# Replace block 1
b1 = """<<<<<<< HEAD
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

    def __init__(
        self,
        logs_dir: Path,
        prompt_template_path: Path | str | None = None,
        version: str | None = None,
        branch: str | None = None,
        commit: str | None = None,
        tag: str | None = None,
        settings_path: str | Path | None = None,
        credentials_path: str | Path | None = None,
        extensions: list[str] | None = None,
        repo_url: str | None = None,
        *args,
        **kwargs,
    ):
        \"\"\"
        Initialize the Gemini CLI agent.

        Args:
            logs_dir: Directory to store logs.
            prompt_template_path: Path to the prompt template.
            version: Version of the agent.
            branch: Branch to clone.
            commit: Commit hash to checkout.
            tag: Tag to checkout.
            settings_path: Path to a local settings.json file to upload to
                ~/.gemini/settings.json.
            credentials_path: Path to a local credentials file to upload to
                ~/.gemini/application_default_credentials.json. If not provided,
                it will try to use the GOOGLE_APPLICATION_CREDENTIALS env var
                or the default gcloud credentials location.
            extensions: List of extensions to install via gemini extensions install.
            repo_url: Custom repository URL to use when downloading the Gemini CLI.
            *args: Additional arguments passed to BaseInstalledAgent.
            **kwargs: Additional keyword arguments passed to BaseInstalledAgent.
        \"\"\"
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

        # Validate mutual exclusivity of branch, commit, and tag
        # Note: self.branch() returns the branch passed to __init__
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
                # Allow standard characters for npm packages, URLs, and GitHub repos
                # Disallow spaces and shell metacharacters
                if not re.match(r"^[a-zA-Z0-9\-_\\.\\/\\:\\@\\~]+\\Z", ext):
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

        self._credentials_path: Path | None = None
        if credentials_path:
            self._credentials_path = Path(credentials_path)
        elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            self._credentials_path = Path(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
        else:
            # Default gcloud credentials location
            default_creds = Path.home() / ".config/gcloud/application_default_credentials.json"
            if default_creds.exists():
                self._credentials_path = default_creds
        
        if self._credentials_path and not self._credentials_path.exists():
             warnings.warn(f"Credentials file not found: {self._credentials_path}")
             self._credentials_path = None
        
        # This will hold the path inside the container after setup
        self._container_credentials_path: str | None = None
        self._python_interpreter: str | None = "python3"

    async def setup(self, environment: BaseEnvironment) -> None:
        \"\"\"
        Setup the agent in the environment. Handles host-side preparation for
        branch-based installations and container-side configuration.
        \"\"\"
        self._bundle_uploaded = False

        if (self.branch() or self._commit or self._tag) and isinstance(environment, DockerEnvironment):
            await self._handle_host_side_setup(environment)

        await self._setup_container_git_credentials(environment)
        await super().setup(environment)
        await self._setup_telemetry_stack(environment)
        await self._setup_container_environment(environment)

        await self._discover_python_interpreter(environment)

    async def _setup_container_git_credentials(self, environment: BaseEnvironment) -> None:
        \"\"\"Securely provisions git credentials in the container without exposing in CLI logs.\"\"\"
        eval_token = os.environ.get("EVAL_REPO_TOKEN")
        repo_url = self._repo_url or "https://github.com/google-gemini/gemini-cli.git"
        if eval_token and repo_url.startswith("https://"):
            domain_part = repo_url.split("https://", 1)[1].split("/")[0]
            if "@" in domain_part:
                domain_part = domain_part.split("@", 1)[1]
            creds_content = f"https://oauth2:{eval_token}@{domain_part}\\n"
            
            home_result = await environment.exec("echo $HOME")
            if home_result.stdout:
                lines = [line.strip() for line in home_result.stdout.strip().splitlines() if line.strip()]
                container_home = lines[-1] if lines else "/root"
            else:
                container_home = "/root"
            
            target_creds_path = f"{container_home}/.git-credentials"
            
            # Write to a secure temporary file on host, upload it, then configure git
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
                tf.write(creds_content)
                temp_creds_path = Path(tf.name)
            
            try:
                temp_creds_path.chmod(0o600)
                await environment.upload_file(
                    source_path=temp_creds_path,
                    target_path=target_creds_path
                )
                await environment.exec("git config --global credential.helper store")
            except Exception as e:
                self.logger.warning(f"Failed to securely push git credentials: {e}")
            finally:
                if temp_creds_path.exists():
                    temp_creds_path.unlink()

    async def _discover_python_interpreter(self, environment: BaseEnvironment) -> None:
        \"\"\"Discovers the best available python interpreter in the container.\"\"\"
        self._python_interpreter = None
        
        candidates_str = " ".join(self._PYTHON_CANDIDATES)
        probe_cmd = (
            f"for p in {candidates_str}; do "
            "if command -v $p >/dev/null 2>&1; then echo \\\"__HARBOR_PYTHON__:$p\\\"; break; fi; "
            "done"
        )
        
        result = await environment.exec(probe_cmd)
        if result.return_code == 0 and result.stdout:
            for line in result.stdout.splitlines():
                if "__HARBOR_PYTHON__:" in line:
                    self._python_interpreter = line.split("__HARBOR_PYTHON__:")[-1].strip()
                    break

        if not self._python_interpreter:
            self.logger.warning(
                "No python interpreter found in container. Telemetry collector will be disabled."
            )

    async def _setup_telemetry_stack(self, environment: BaseEnvironment) -> None:
        \"\"\"Uploads the telemetry stack to the container.\"\"\"
        telemetry_dir = Path(__file__).parent / "gemini_cli_telemetry"
        if telemetry_dir.exists():
            await environment.upload_dir(
                source_dir=telemetry_dir,
                target_dir="/installed-agent/telemetry",
            )

    async def _handle_host_side_setup(self, environment: BaseEnvironment) -> None:
        \"\"\"Coordination for host-side preparation and bundle transfer.\"\"\"
        host_path = Path("~/.cache/harbor/shared_agent").expanduser().resolve()
        
        # Avoid re-entering the synchronized block if already done
        if GeminiCli._host_setup_done:
            if GeminiCli._agent_commit_id:
                await self._upload_and_unpack_bundle(
                    environment, host_path, GeminiCli._agent_commit_id
                )
            return

        async with self._host_setup_lock:
            if not GeminiCli._host_setup_done:
                branch = self.branch()
                if branch or self._commit or self._tag:
                    host_path.mkdir(parents=True, exist_ok=True)
                    await self._prepare_host_repo(
                        host_path, branch=branch, commit=self._commit, tag=self._tag
                    )
                    
                    if not GeminiCli._agent_commit_id:
                        stdout, _ = await self._run_host_cmd(["git", "rev-parse", "HEAD"], cwd=host_path)
                        GeminiCli._agent_commit_id = stdout.strip()

                    await self._build_host_bundle(host_path)
                
                # Mark as done regardless of whether a branch was provided,
                # as the host-side setup attempt is complete for the process.
                GeminiCli._host_setup_done = True

            if GeminiCli._agent_commit_id:
                await self._upload_and_unpack_bundle(
                    environment, host_path, GeminiCli._agent_commit_id
                )

    async def _run_host_cmd(self, args: list[str], cwd: Path, mask_token: str | None = None) -> tuple[str, str]:
        \"\"\"Runs a command on the host and returns (stdout, stderr).\"\"\"
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            cmd_str = " ".join(args)
            stdout_str = stdout.decode()
            stderr_str = stderr.decode()
            
            if mask_token:
                cmd_str = cmd_str.replace(mask_token, "***")
                stdout_str = stdout_str.replace(mask_token, "***")
                stderr_str = stderr_str.replace(mask_token, "***")
                
            self.logger.error(f"[Host] '{cmd_str}' failed with exit code {proc.returncode}")
            self.logger.error(f"[Host] stdout: {stdout_str}")
            self.logger.error(f"[Host] stderr: {stderr_str}")
            raise RuntimeError(f"Command '{cmd_str}' failed")
        return stdout.decode(), stderr.decode()

    async def _prepare_host_repo(
        self,
        host_path: Path,
        branch: str | None = None,
        commit: str | None = None,
        tag: str | None = None,
    ) -> None:
        \"\"\"Prepares the repository on the host (async).\"\"\"
        repo_url = self._repo_url or "https://github.com/google-gemini/gemini-cli.git"
        eval_token = os.environ.get("EVAL_REPO_TOKEN")

        clone_url = repo_url
        if eval_token and clone_url.startswith("https://"):
            # Inject token temporarily for operations
            if "@" not in clone_url.split("https://", 1)[1].split("/")[0]:
                clone_url = clone_url.replace("https://", f"https://{eval_token}@", 1)

        try:
            if not (host_path / ".git").exists():
                await self._run_host_cmd(["git", "clone", clone_url, "."], cwd=host_path, mask_token=eval_token)
            else:
                await self._run_host_cmd(["git", "remote", "set-url", "origin", clone_url], cwd=host_path, mask_token=eval_token)

            # Fetch
            await self._run_host_cmd(["git", "fetch", "origin"], cwd=host_path, mask_token=eval_token)

            if commit:
                await self._run_host_cmd(["git", "checkout", "-f", commit], cwd=host_path, mask_token=eval_token)
            elif tag:
                await self._run_host_cmd(
                    ["git", "checkout", "-f", f"tags/{tag}"], cwd=host_path, mask_token=eval_token
                )
            elif branch:
                # Checkout
                await self._run_host_cmd(["git", "checkout", "-f", branch], cwd=host_path, mask_token=eval_token)
                # Pull
                try:
                    await self._run_host_cmd(
                        ["git", "pull", "origin", branch], cwd=host_path, mask_token=eval_token
                    )
                except RuntimeError:
                    self.logger.warning(
                        f"[Host] git pull failed, resetting hard to origin/{branch}"
                    )
                    await self._run_host_cmd(
                        ["git", "reset", "--hard", f"origin/{branch}"], cwd=host_path, mask_token=eval_token
                    )
        finally:
            # Revert the remote URL to ensure the token doesn't persist in .git/config
            if (host_path / ".git").exists():
                try:
                    await self._run_host_cmd(["git", "remote", "set-url", "origin", repo_url], cwd=host_path)
                except Exception as cleanup_err:
                    self.logger.warning(
                        f"Failed to cleanly revert repository remote URL to '{repo_url}'. "
                        f"This may leave the temporary credentials in the local cache. Error: {cleanup_err}"
                    )

    async def _build_host_bundle(self, host_path: Path) -> None:
        \"\"\"Runs the build and bundle commands on the host (async).\"\"\"
        
        try:
            await self._run_host_cmd(["npm", "install", "--ignore-scripts", "--no-audit", "--no-fund"], cwd=host_path)
            await self._run_host_cmd(["npm", "run", "bundle"], cwd=host_path)
            
            # Skills pathing fix
            skills_dir = host_path / "bundle" / "src" / "skills"
            skills_dir.mkdir(parents=True, exist_ok=True)
            builtin_link = skills_dir / "builtin"
            if not builtin_link.exists():
                os.symlink("../../builtin", builtin_link)
        except Exception:
            raise

    async def _upload_and_unpack_bundle(
        self, environment: BaseEnvironment, host_path: Path, commit_id: str
    ) -> None:
        \"\"\"Transfers the pre-built bundle from host to container.\"\"\"
        tarball_name = f"gemini-bundle-{commit_id}.tar.gz"
        host_tarball_path = host_path / tarball_name
        
        if not host_tarball_path.exists():
            def create_tar():
                with tarfile.open(host_tarball_path, "w:gz") as tar:
                    tar.add(host_path / "bundle", arcname="bundle")
                    if (host_path / "package.json").exists():
                        tar.add(host_path / "package.json", arcname="package.json")
            
            await asyncio.to_thread(create_tar)

        container_tarball_path = f"/tmp/{tarball_name}"
        await environment.upload_file(
            source_path=host_tarball_path,
            target_path=container_tarball_path,
        )
        
        await environment.exec(
            f"mkdir -p ~/gemini-cli && tar -xzf {container_tarball_path} -C ~/gemini-cli"
        )
        self._bundle_uploaded = True

    async def _setup_container_environment(self, environment: BaseEnvironment) -> None:
        \"\"\"Configures the container environment (trust, settings, credentials).\"\"\"
        await self._setup_folder_trust(environment)
        if self._settings_path:
            await self._setup_settings(environment)
        if self._credentials_path:
            await self._setup_credentials(environment)

    async def _setup_folder_trust(self, environment: BaseEnvironment) -> None:
        \"\"\"Configures folder trust in the container.\"\"\"
        # Trust the testbed folder
        trust_setup_cmd = (
            "mkdir -p ~/.gemini && "
            "echo '{\\"/testbed\\": \\"TRUST_FOLDER\\"}' > ~/.gemini/trustedFolders.json"
        )
        try:
            await environment.exec(trust_setup_cmd)
        except Exception as e:
            raise RuntimeError(f"Failed to setup folder trust: {e}")

    async def _setup_settings(self, environment: BaseEnvironment) -> None:
        \"\"\"Uploads and moves settings.json to the correct container path.\"\"\"
        # environment.upload_file (docker cp) does not expand ~
        # We upload to /tmp first then use a shell command to move it to ~/.gemini/
        temp_path = f"/tmp/settings-{uuid.uuid4()}"
        await environment.upload_file(
            source_path=self._settings_path,
            target_path=temp_path,
        )
        await environment.exec(
            f"mkdir -p ~/.gemini && mv {shlex.quote(temp_path)} ~/.gemini/settings.json"
        )

    async def _setup_credentials(self, environment: BaseEnvironment) -> None:
        \"\"\"Uploads and moves credentials to the correct container path.\"\"\"
        # We capture the $HOME dir to set an absolute path for the credentials
        home_result = await environment.exec("echo $HOME")
        if home_result.stdout:
            lines = [line.strip() for line in home_result.stdout.strip().splitlines() if line.strip()]
            container_home = lines[-1] if lines else "/root"
        else:
            container_home = "/root"
        
        temp_creds_path = f"/tmp/creds-{uuid.uuid4()}"
        await environment.upload_file(
            source_path=self._credentials_path,
            target_path=temp_creds_path,
        )
        
        target_creds_path = f"{container_home}/.gemini/application_default_credentials.json"
        await environment.exec(
            f"mkdir -p {container_home}/.gemini && mv {shlex.quote(temp_creds_path)} {target_creds_path}"
        )
        self._container_credentials_path = target_creds_path

=======
    def get_version_command(self) -> str | None:
        return ". ~/.nvm/nvm.sh; gemini --version"

    SUPPORTS_ATIF: bool = True

    CLI_FLAGS = [
        CliFlag(
            "sandbox",
            cli="--sandbox",
            type="bool",
        ),
    ]

    # Counter for generating unique image filenames within a session
    _image_counter: int = 0
>>>>>>> upstream/main"""

r1 = """    def get_version_command(self) -> str | None:
        return ". ~/.nvm/nvm.sh; gemini --version"

    SUPPORTS_ATIF: bool = True

    CLI_FLAGS = [
        CliFlag(
            "sandbox",
            cli="--sandbox",
            type="bool",
        ),
    ]

    # Counter for generating unique image filenames within a session
    _image_counter: int = 0

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

    def __init__(
        self,
        logs_dir: Path,
        prompt_template_path: Path | str | None = None,
        version: str | None = None,
        branch: str | None = None,
        commit: str | None = None,
        tag: str | None = None,
        settings_path: str | Path | None = None,
        credentials_path: str | Path | None = None,
        extensions: list[str] | None = None,
        repo_url: str | None = None,
        *args,
        **kwargs,
    ):
        \"\"\"
        Initialize the Gemini CLI agent.

        Args:
            logs_dir: Directory to store logs.
            prompt_template_path: Path to the prompt template.
            version: Version of the agent.
            branch: Branch to clone.
            commit: Commit hash to checkout.
            tag: Tag to checkout.
            settings_path: Path to a local settings.json file to upload to
                ~/.gemini/settings.json.
            credentials_path: Path to a local credentials file to upload to
                ~/.gemini/application_default_credentials.json. If not provided,
                it will try to use the GOOGLE_APPLICATION_CREDENTIALS env var
                or the default gcloud credentials location.
            extensions: List of extensions to install via gemini extensions install.
            repo_url: Custom repository URL to use when downloading the Gemini CLI.
            *args: Additional arguments passed to BaseInstalledAgent.
            **kwargs: Additional keyword arguments passed to BaseInstalledAgent.
        \"\"\"
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

        # Validate mutual exclusivity of branch, commit, and tag
        # Note: self.branch() returns the branch passed to __init__
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
                # Allow standard characters for npm packages, URLs, and GitHub repos
                # Disallow spaces and shell metacharacters
                if not re.match(r"^[a-zA-Z0-9\-_\\.\\/\\:\\@\\~]+\\Z", ext):
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

        self._credentials_path: Path | None = None
        if credentials_path:
            self._credentials_path = Path(credentials_path)
        elif os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            self._credentials_path = Path(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
        else:
            # Default gcloud credentials location
            default_creds = Path.home() / ".config/gcloud/application_default_credentials.json"
            if default_creds.exists():
                self._credentials_path = default_creds
        
        if self._credentials_path and not self._credentials_path.exists():
             warnings.warn(f"Credentials file not found: {self._credentials_path}")
             self._credentials_path = None
        
        # This will hold the path inside the container after setup
        self._container_credentials_path: str | None = None
        self._python_interpreter: str | None = "python3"

    async def setup(self, environment: BaseEnvironment) -> None:
        \"\"\"
        Setup the agent in the environment. Handles host-side preparation for
        branch-based installations and container-side configuration.
        \"\"\"
        self._bundle_uploaded = False

        if (self.branch() or self._commit or self._tag) and isinstance(environment, DockerEnvironment):
            await self._handle_host_side_setup(environment)

        await self._setup_container_git_credentials(environment)
        await super().setup(environment)
        await self._setup_telemetry_stack(environment)
        await self._setup_container_environment(environment)

        await self._discover_python_interpreter(environment)

    async def _setup_container_git_credentials(self, environment: BaseEnvironment) -> None:
        \"\"\"Securely provisions git credentials in the container without exposing in CLI logs.\"\"\"
        eval_token = os.environ.get("EVAL_REPO_TOKEN")
        repo_url = self._repo_url or "https://github.com/google-gemini/gemini-cli.git"
        if eval_token and repo_url.startswith("https://"):
            domain_part = repo_url.split("https://", 1)[1].split("/")[0]
            if "@" in domain_part:
                domain_part = domain_part.split("@", 1)[1]
            creds_content = f"https://oauth2:{eval_token}@{domain_part}\\n"
            
            home_result = await environment.exec("echo $HOME")
            if home_result.stdout:
                lines = [line.strip() for line in home_result.stdout.strip().splitlines() if line.strip()]
                container_home = lines[-1] if lines else "/root"
            else:
                container_home = "/root"
            
            target_creds_path = f"{container_home}/.git-credentials"
            
            # Write to a secure temporary file on host, upload it, then configure git
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
                tf.write(creds_content)
                temp_creds_path = Path(tf.name)
            
            try:
                temp_creds_path.chmod(0o600)
                await environment.upload_file(
                    source_path=temp_creds_path,
                    target_path=target_creds_path
                )
                await environment.exec("git config --global credential.helper store")
            except Exception as e:
                self.logger.warning(f"Failed to securely push git credentials: {e}")
            finally:
                if temp_creds_path.exists():
                    temp_creds_path.unlink()

    async def _discover_python_interpreter(self, environment: BaseEnvironment) -> None:
        \"\"\"Discovers the best available python interpreter in the container.\"\"\"
        self._python_interpreter = None
        
        candidates_str = " ".join(self._PYTHON_CANDIDATES)
        probe_cmd = (
            f"for p in {candidates_str}; do "
            "if command -v $p >/dev/null 2>&1; then echo \\\"__HARBOR_PYTHON__:$p\\\"; break; fi; "
            "done"
        )
        
        result = await environment.exec(probe_cmd)
        if result.return_code == 0 and result.stdout:
            for line in result.stdout.splitlines():
                if "__HARBOR_PYTHON__:" in line:
                    self._python_interpreter = line.split("__HARBOR_PYTHON__:")[-1].strip()
                    break

        if not self._python_interpreter:
            self.logger.warning(
                "No python interpreter found in container. Telemetry collector will be disabled."
            )

    async def _setup_telemetry_stack(self, environment: BaseEnvironment) -> None:
        \"\"\"Uploads the telemetry stack to the container.\"\"\"
        telemetry_dir = Path(__file__).parent / "gemini_cli_telemetry"
        if telemetry_dir.exists():
            await environment.upload_dir(
                source_dir=telemetry_dir,
                target_dir="/installed-agent/telemetry",
            )

    async def _handle_host_side_setup(self, environment: BaseEnvironment) -> None:
        \"\"\"Coordination for host-side preparation and bundle transfer.\"\"\"
        host_path = Path("~/.cache/harbor/shared_agent").expanduser().resolve()
        
        # Avoid re-entering the synchronized block if already done
        if GeminiCli._host_setup_done:
            if GeminiCli._agent_commit_id:
                await self._upload_and_unpack_bundle(
                    environment, host_path, GeminiCli._agent_commit_id
                )
            return

        async with self._host_setup_lock:
            if not GeminiCli._host_setup_done:
                branch = self.branch()
                if branch or self._commit or self._tag:
                    host_path.mkdir(parents=True, exist_ok=True)
                    await self._prepare_host_repo(
                        host_path, branch=branch, commit=self._commit, tag=self._tag
                    )
                    
                    if not GeminiCli._agent_commit_id:
                        stdout, _ = await self._run_host_cmd(["git", "rev-parse", "HEAD"], cwd=host_path)
                        GeminiCli._agent_commit_id = stdout.strip()

                    await self._build_host_bundle(host_path)
                
                # Mark as done regardless of whether a branch was provided,
                # as the host-side setup attempt is complete for the process.
                GeminiCli._host_setup_done = True

            if GeminiCli._agent_commit_id:
                await self._upload_and_unpack_bundle(
                    environment, host_path, GeminiCli._agent_commit_id
                )

    async def _run_host_cmd(self, args: list[str], cwd: Path, mask_token: str | None = None) -> tuple[str, str]:
        \"\"\"Runs a command on the host and returns (stdout, stderr).\"\"\"
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            cmd_str = " ".join(args)
            stdout_str = stdout.decode()
            stderr_str = stderr.decode()
            
            if mask_token:
                cmd_str = cmd_str.replace(mask_token, "***")
                stdout_str = stdout_str.replace(mask_token, "***")
                stderr_str = stderr_str.replace(mask_token, "***")
                
            self.logger.error(f"[Host] '{cmd_str}' failed with exit code {proc.returncode}")
            self.logger.error(f"[Host] stdout: {stdout_str}")
            self.logger.error(f"[Host] stderr: {stderr_str}")
            raise RuntimeError(f"Command '{cmd_str}' failed")
        return stdout.decode(), stderr.decode()

    async def _prepare_host_repo(
        self,
        host_path: Path,
        branch: str | None = None,
        commit: str | None = None,
        tag: str | None = None,
    ) -> None:
        \"\"\"Prepares the repository on the host (async).\"\"\"
        repo_url = self._repo_url or "https://github.com/google-gemini/gemini-cli.git"
        eval_token = os.environ.get("EVAL_REPO_TOKEN")

        clone_url = repo_url
        if eval_token and clone_url.startswith("https://"):
            # Inject token temporarily for operations
            if "@" not in clone_url.split("https://", 1)[1].split("/")[0]:
                clone_url = clone_url.replace("https://", f"https://{eval_token}@", 1)

        try:
            if not (host_path / ".git").exists():
                await self._run_host_cmd(["git", "clone", clone_url, "."], cwd=host_path, mask_token=eval_token)
            else:
                await self._run_host_cmd(["git", "remote", "set-url", "origin", clone_url], cwd=host_path, mask_token=eval_token)

            # Fetch
            await self._run_host_cmd(["git", "fetch", "origin"], cwd=host_path, mask_token=eval_token)

            if commit:
                await self._run_host_cmd(["git", "checkout", "-f", commit], cwd=host_path, mask_token=eval_token)
            elif tag:
                await self._run_host_cmd(
                    ["git", "checkout", "-f", f"tags/{tag}"], cwd=host_path, mask_token=eval_token
                )
            elif branch:
                # Checkout
                await self._run_host_cmd(["git", "checkout", "-f", branch], cwd=host_path, mask_token=eval_token)
                # Pull
                try:
                    await self._run_host_cmd(
                        ["git", "pull", "origin", branch], cwd=host_path, mask_token=eval_token
                    )
                except RuntimeError:
                    self.logger.warning(
                        f"[Host] git pull failed, resetting hard to origin/{branch}"
                    )
                    await self._run_host_cmd(
                        ["git", "reset", "--hard", f"origin/{branch}"], cwd=host_path, mask_token=eval_token
                    )
        finally:
            # Revert the remote URL to ensure the token doesn't persist in .git/config
            if (host_path / ".git").exists():
                try:
                    await self._run_host_cmd(["git", "remote", "set-url", "origin", repo_url], cwd=host_path)
                except Exception as cleanup_err:
                    self.logger.warning(
                        f"Failed to cleanly revert repository remote URL to '{repo_url}'. "
                        f"This may leave the temporary credentials in the local cache. Error: {cleanup_err}"
                    )

    async def _build_host_bundle(self, host_path: Path) -> None:
        \"\"\"Runs the build and bundle commands on the host (async).\"\"\"
        
        try:
            await self._run_host_cmd(["npm", "install", "--ignore-scripts", "--no-audit", "--no-fund"], cwd=host_path)
            await self._run_host_cmd(["npm", "run", "bundle"], cwd=host_path)
            
            # Skills pathing fix
            skills_dir = host_path / "bundle" / "src" / "skills"
            skills_dir.mkdir(parents=True, exist_ok=True)
            builtin_link = skills_dir / "builtin"
            if not builtin_link.exists():
                os.symlink("../../builtin", builtin_link)
        except Exception:
            raise

    async def _upload_and_unpack_bundle(
        self, environment: BaseEnvironment, host_path: Path, commit_id: str
    ) -> None:
        \"\"\"Transfers the pre-built bundle from host to container.\"\"\"
        tarball_name = f"gemini-bundle-{commit_id}.tar.gz"
        host_tarball_path = host_path / tarball_name
        
        if not host_tarball_path.exists():
            def create_tar():
                with tarfile.open(host_tarball_path, "w:gz") as tar:
                    tar.add(host_path / "bundle", arcname="bundle")
                    if (host_path / "package.json").exists():
                        tar.add(host_path / "package.json", arcname="package.json")
            
            await asyncio.to_thread(create_tar)

        container_tarball_path = f"/tmp/{tarball_name}"
        await environment.upload_file(
            source_path=host_tarball_path,
            target_path=container_tarball_path,
        )
        
        await environment.exec(
            f"mkdir -p ~/gemini-cli && tar -xzf {container_tarball_path} -C ~/gemini-cli"
        )
        self._bundle_uploaded = True

    async def _setup_container_environment(self, environment: BaseEnvironment) -> None:
        \"\"\"Configures the container environment (trust, settings, credentials).\"\"\"
        await self._setup_folder_trust(environment)
        if self._settings_path:
            await self._setup_settings(environment)
        if self._credentials_path:
            await self._setup_credentials(environment)

    async def _setup_folder_trust(self, environment: BaseEnvironment) -> None:
        \"\"\"Configures folder trust in the container.\"\"\"
        # Trust the testbed folder
        trust_setup_cmd = (
            "mkdir -p ~/.gemini && "
            "echo '{\\"/testbed\\": \\"TRUST_FOLDER\\"}' > ~/.gemini/trustedFolders.json"
        )
        try:
            await environment.exec(trust_setup_cmd)
        except Exception as e:
            raise RuntimeError(f"Failed to setup folder trust: {e}")

    async def _setup_settings(self, environment: BaseEnvironment) -> None:
        \"\"\"Uploads and moves settings.json to the correct container path.\"\"\"
        # environment.upload_file (docker cp) does not expand ~
        # We upload to /tmp first then use a shell command to move it to ~/.gemini/
        temp_path = f"/tmp/settings-{uuid.uuid4()}"
        await environment.upload_file(
            source_path=self._settings_path,
            target_path=temp_path,
        )
        await environment.exec(
            f"mkdir -p ~/.gemini && mv {shlex.quote(temp_path)} ~/.gemini/settings.json"
        )

    async def _setup_credentials(self, environment: BaseEnvironment) -> None:
        \"\"\"Uploads and moves credentials to the correct container path.\"\"\"
        # We capture the $HOME dir to set an absolute path for the credentials
        home_result = await environment.exec("echo $HOME")
        if home_result.stdout:
            lines = [line.strip() for line in home_result.stdout.strip().splitlines() if line.strip()]
            container_home = lines[-1] if lines else "/root"
        else:
            container_home = "/root"
        
        temp_creds_path = f"/tmp/creds-{uuid.uuid4()}"
        await environment.upload_file(
            source_path=self._credentials_path,
            target_path=temp_creds_path,
        )
        
        target_creds_path = f"{container_home}/.gemini/application_default_credentials.json"
        await environment.exec(
            f"mkdir -p {container_home}/.gemini && mv {shlex.quote(temp_creds_path)} {target_creds_path}"
        )
        self._container_credentials_path = target_creds_path
"""
if b1 in text:
    text = text.replace(b1, r1)


b2 = """<<<<<<< HEAD
    @property
    def _template_variables(self) -> dict[str, Any]:
        variables: dict[str, Any] = super()._template_variables
        if self._extensions:
            variables["extensions"] = [shlex.quote(ext) for ext in self._extensions]
        if hasattr(self, "_bundle_uploaded") and self._bundle_uploaded:
            variables["bundle_uploaded"] = True
        if self._commit:
            variables["commit"] = self._commit
        if self._tag:
            variables["tag"] = self._tag
        
        repo_url = getattr(self, "_repo_url", None) or "https://github.com/google-gemini/gemini-cli.git"
        variables["repo_url"] = repo_url

        variables["python_candidates"] = self._PYTHON_CANDIDATES
        return variables

    def _convert_gemini_to_atif(self, gemini_trajectory: dict[str, Any]) -> Trajectory | None:
=======
    def _save_image(
        self,
        image_data: str,
        mime_type: str,
        step_id: int,
        obs_index: int,
        image_index: int = 0,
    ) -> tuple[str, _ImageMediaType] | tuple[None, None]:
        \"\"\"Save a base64 image to the images directory.

        Args:
            image_data: Base64-encoded image data
            mime_type: MIME type of the image (e.g., 'image/png')
            step_id: The step ID this image belongs to
            obs_index: Index of the observation result within the step
            image_index: Index of the image within the observation (for multiple images)

        Returns:
            Tuple of (relative_path, media_type) for the saved image, or (None, None) on failure
        \"\"\"
        # Create images directory if it doesn't exist
        images_dir = self.logs_dir / "images"
        images_dir.mkdir(exist_ok=True)

        # Determine file extension from mime type
        # Only accept MIME types that ImageSource validates
        extension_map: dict[_ImageMediaType, str] = {
            "image/png": "png",
            "image/jpeg": "jpg",
            "image/gif": "gif",
            "image/webp": "webp",
        }
        
        # Fast validation: if mime_type is not supported, ignore immediately
        if mime_type not in extension_map:
            self.logger.warning(f"Unsupported image format in trajectory: {mime_type}")
            return None, None
            
        media_type: _ImageMediaType = mime_type  # type: ignore

        # Clean base64 data if it contains data URI scheme prefix
        if "," in image_data:
            image_data = image_data.split(",")[1]

        # Generate unique filename for this image
        filename = f"step_{step_id}_obs_{obs_index}_img_{image_index}.{extension_map[media_type]}"
        relative_path = f"images/{filename}"
        full_path = images_dir / filename

        try:
            # Decode and write to file
            image_bytes = base64.b64decode(image_data)
            full_path.write_bytes(image_bytes)
            return relative_path, media_type
        except Exception as e:
            self.logger.error(f"Failed to save image {filename}: {e}")
            return None, None

    def _convert_gemini_to_atif(self, gemini_trajectory: dict[str, Any]) -> Trajectory | None:
>>>>>>> upstream/main"""

r2 = """    @property
    def _template_variables(self) -> dict[str, Any]:
        variables: dict[str, Any] = super()._template_variables
        if self._extensions:
            variables["extensions"] = [shlex.quote(ext) for ext in self._extensions]
        if hasattr(self, "_bundle_uploaded") and self._bundle_uploaded:
            variables["bundle_uploaded"] = True
        if self._commit:
            variables["commit"] = self._commit
        if self._tag:
            variables["tag"] = self._tag
        
        repo_url = getattr(self, "_repo_url", None) or "https://github.com/google-gemini/gemini-cli.git"
        variables["repo_url"] = repo_url

        variables["python_candidates"] = self._PYTHON_CANDIDATES
        return variables

    def _save_image(
        self,
        image_data: str,
        mime_type: str,
        step_id: int,
        obs_index: int,
        image_index: int = 0,
    ) -> tuple[str, _ImageMediaType] | tuple[None, None]:
        \"\"\"Save a base64 image to the images directory.

        Args:
            image_data: Base64-encoded image data
            mime_type: MIME type of the image (e.g., 'image/png')
            step_id: The step ID this image belongs to
            obs_index: Index of the observation result within the step
            image_index: Index of the image within the observation (for multiple images)

        Returns:
            Tuple of (relative_path, media_type) for the saved image, or (None, None) on failure
        \"\"\"
        # Create images directory if it doesn't exist
        images_dir = self.logs_dir / "images"
        images_dir.mkdir(exist_ok=True)

        # Determine file extension from mime type
        # Only accept MIME types that ImageSource validates
        extension_map: dict[_ImageMediaType, str] = {
            "image/png": "png",
            "image/jpeg": "jpg",
            "image/gif": "gif",
            "image/webp": "webp",
        }
        
        # Fast validation: if mime_type is not supported, ignore immediately
        if mime_type not in extension_map:
            self.logger.warning(f"Unsupported image format in trajectory: {mime_type}")
            return None, None
            
        media_type: _ImageMediaType = mime_type  # type: ignore

        # Clean base64 data if it contains data URI scheme prefix
        if "," in image_data:
            image_data = image_data.split(",")[1]

        # Generate unique filename for this image
        filename = f"step_{step_id}_obs_{obs_index}_img_{image_index}.{extension_map[media_type]}"
        relative_path = f"images/{filename}"
        full_path = images_dir / filename

        try:
            # Decode and write to file
            image_bytes = base64.b64decode(image_data)
            full_path.write_bytes(image_bytes)
            return relative_path, media_type
        except Exception as e:
            self.logger.error(f"Failed to save image {filename}: {e}")
            return None, None

    def _convert_gemini_to_atif(self, gemini_trajectory: dict[str, Any]) -> Trajectory | None:"""
if b2 in text:
    text = text.replace(b2, r2)


b3 = """<<<<<<< HEAD
        The trajectory file is written to ~/.gemini/tmp inside the container.
        We copy it to /logs/agent/gemini-cli.trajectory.json so it persists and can be
        downloaded.
        \"\"\"
        try:
            await environment.exec(f"mkdir -p {self.logs_dir}")
            # Run the base implementation which executes the agent commands
            await super().run(instruction, environment, context)
        finally:
            # Always try to copy the trajectory file, even if the agent timed out
            copy_command = (
                "find ~/.gemini/tmp -type f -name 'session-*.json' 2>/dev/null | "
                "head -n 1 | xargs -r -I{} cp {} /logs/agent/gemini-cli.trajectory.json"
            )
            # 2. Copy Telemetry (Add this block)
            # This handles cases where the ENV var was ignored or written to a tmp location
            copy_telemetry_command = (
                "find ~/.gemini/tmp -type f -name 'telemetry-*.json' 2>/dev/null | "
                "head -n 1 | xargs -r -I{} cp {} /logs/agent/gemini-cli.telemetry.json"
            )

            # If the ENV var worked and wrote to a different unmounted dir, try copying from there too:
            # (Optional redundancy if you want to be safe)
            if str(self.logs_dir) != "/logs/agent":
                 copy_telemetry_command += (
                     f" || cp {self.logs_dir}/gemini-cli.telemetry.json /logs/agent/gemini-cli.telemetry.json 2>/dev/null"
                 )
            try:
                await environment.exec(command=f"{copy_command} ; {copy_telemetry_command}")
            except Exception as e:
                print(f"Could not copy trajectory file: {e}")
=======
    def _build_register_skills_command(self) -> str | None:
        \"\"\"Return a shell command that copies skills to Gemini CLI's skills directory.\"\"\"
        if not self.skills_dir:
            return None
        return (
            f"mkdir -p ~/.gemini/skills && "
            f"cp -r {shlex.quote(self.skills_dir)}/* "
            f"~/.gemini/skills/ 2>/dev/null || true"
        )

    def _build_register_mcp_servers_command(self) -> str | None:
        \"\"\"Return a shell command that writes MCP config to ~/.gemini/settings.json.\"\"\"
        if not self.mcp_servers:
            return None
        servers: dict[str, dict[str, Any]] = {}
        for server in self.mcp_servers:
            if server.transport == "stdio":
                servers[server.name] = {"command": server.command, "args": server.args}
            elif server.transport == "streamable-http":
                servers[server.name] = {"httpUrl": server.url}
            else:  # sse
                servers[server.name] = {"url": server.url}
        config = json.dumps({"mcpServers": servers}, indent=2)
        escaped = shlex.quote(config)
        return f"mkdir -p ~/.gemini && echo {escaped} > ~/.gemini/settings.json"
>>>>>>> upstream/main"""

r3 = """    def create_cleanup_commands(self) -> list[ExecInput]:
        copy_command = (
            "find ~/.gemini/tmp -type f -name 'session-*.json' 2>/dev/null | "
            "head -n 1 | xargs -r -I{} cp {} /logs/agent/gemini-cli.trajectory.json"
        )
        # 2. Copy Telemetry (Add this block)
        # This handles cases where the ENV var was ignored or written to a tmp location
        copy_telemetry_command = (
            "find ~/.gemini/tmp -type f -name 'telemetry-*.json' 2>/dev/null | "
            "head -n 1 | xargs -r -I{} cp {} /logs/agent/gemini-cli.telemetry.json"
        )

        # If the ENV var worked and wrote to a different unmounted dir, try copying from there too:
        # (Optional redundancy if you want to be safe)
        if str(self.logs_dir) != "/logs/agent":
            copy_telemetry_command += (
                f" || cp {self.logs_dir}/gemini-cli.telemetry.json /logs/agent/gemini-cli.telemetry.json 2>/dev/null"
            )
        
        return [
            ExecInput(
                command=f"{copy_command} ; {copy_telemetry_command}",
            ),
        ]

    def _build_register_skills_command(self) -> str | None:
        \"\"\"Return a shell command that copies skills to Gemini CLI's skills directory.\"\"\"
        if not self.skills_dir:
            return None
        return (
            f"mkdir -p ~/.gemini/skills && "
            f"cp -r {shlex.quote(self.skills_dir)}/* "
            f"~/.gemini/skills/ 2>/dev/null || true"
        )

    def _build_register_mcp_servers_command(self) -> str | None:
        \"\"\"Return a shell command that writes MCP config to ~/.gemini/settings.json.\"\"\"
        if not self.mcp_servers:
            return None
        servers: dict[str, dict[str, Any]] = {}
        for server in self.mcp_servers:
            if server.transport == "stdio":
                servers[server.name] = {"command": server.command, "args": server.args}
            elif server.transport == "streamable-http":
                servers[server.name] = {"httpUrl": server.url}
            else:  # sse
                servers[server.name] = {"url": server.url}
        config = json.dumps({"mcpServers": servers}, indent=2)
        escaped = shlex.quote(config)
        return f"mkdir -p ~/.gemini && echo {escaped} > ~/.gemini/settings.json" """

# Also we need to strip `def create_cleanup_commands(self) -> list[ExecInput]:` block that was before block 3.
# Wait, let's just use string replacement on block3, and later clean up if there are two `create_cleanup_commands`.
if b3 in text:
    text = text.replace(b3, r3)

b4 = """<<<<<<< HEAD
        # Telemetry setup
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

        # Additional documented telemetry options
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

        # Conditional unsetting of OUTFILE
        # Documentation: true or 1 enables boolean features
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
            # Point to local to avoid the CLI trying to export directly to GCP
            # when we want it to go through the collector.
            env["GEMINI_TELEMETRY_TARGET"] = "local"

        if is_gcp or is_collector:
            env.pop("GEMINI_TELEMETRY_OUTFILE", None)

        # Reconstruct the command string:
        # 1) Export variables explicitly. The CLI sometimes overrides process env in
        # specific spawn situations. Sourcing /root/.gemini/env.sh (or similar) inside
        # the container ensures persistence.
        # Here we just prepend them to the command execution.
        telemetry_exports = []
        for k, v in env.items():
            if k.startswith("GEMINI_TELEMETRY_"):
                telemetry_exports.append(f"export {k}='{v}'")
        
        export_cmd = " && ".join(telemetry_exports) + " && " if telemetry_exports else ""
        
        # Determine the base command
        base_cmd = f"gemini"
        
        args = f"do {shlex.quote(instruction)} --verbose"
        
        if self._dataset_name and self._task_name:
            args += f" --run-id {shlex.quote(self._dataset_name)}/{shlex.quote(self._task_name)}"

        if self._model_name:
            args += f" --model {shlex.quote(self._model_name)}"
        if self._prompt_template_path:
            args += f" --prompt-file {shlex.quote(str(self._prompt_template_path))}"

        full_command = f"{export_cmd}{base_cmd} {args}"

        return [
            ExecInput(
                command=full_command,
                env=env,
            )
        ]
=======
        commands: list[ExecInput] = []

        skills_command = self._build_register_skills_command()
        if skills_command:
            commands.append(ExecInput(command=skills_command, env=env))

        mcp_command = self._build_register_mcp_servers_command()
        if mcp_command:
            commands.append(ExecInput(command=mcp_command, env=env))

        cmd = "gemini do"
        cmd += " " + self.build_cli_flags()

        # Build basic command
        if self._model_name:
            cmd += f" --model {shlex.quote(self._model_name)}"
        if self._prompt_template_path:
            cmd += f" --prompt-file {shlex.quote(str(self._prompt_template_path))}"
        cmd += f" {shlex.quote(instruction)}"

        commands.append(
            ExecInput(
                command=cmd,
                env=env,
            )
        )

        return commands
>>>>>>> upstream/main"""

r4 = """        # Telemetry setup
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

        # Additional documented telemetry options
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

        # Conditional unsetting of OUTFILE
        # Documentation: true or 1 enables boolean features
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
            # Point to local to avoid the CLI trying to export directly to GCP
            # when we want it to go through the collector.
            env["GEMINI_TELEMETRY_TARGET"] = "local"

        if is_gcp or is_collector:
            env.pop("GEMINI_TELEMETRY_OUTFILE", None)

        # Reconstruct the command string:
        # 1) Export variables explicitly. The CLI sometimes overrides process env in
        # specific spawn situations. Sourcing /root/.gemini/env.sh (or similar) inside
        # the container ensures persistence.
        # Here we just prepend them to the command execution.
        telemetry_exports = []
        for k, v in env.items():
            if k.startswith("GEMINI_TELEMETRY_"):
                telemetry_exports.append(f"export {k}='{v}'")
        
        export_cmd = " && ".join(telemetry_exports) + " && " if telemetry_exports else ""
        
        commands: list[ExecInput] = []

        skills_command = self._build_register_skills_command()
        if skills_command:
            commands.append(ExecInput(command=skills_command, env=env))

        mcp_command = self._build_register_mcp_servers_command()
        if mcp_command:
            commands.append(ExecInput(command=mcp_command, env=env))

        cmd = "gemini do"
        cmd += " " + self.build_cli_flags()
        
        if getattr(self, "_dataset_name", None) and getattr(self, "_task_name", None):
            cmd += f" --run-id {shlex.quote(self._dataset_name)}/{shlex.quote(self._task_name)}"

        # Build basic command
        if self._model_name:
            cmd += f" --model {shlex.quote(self._model_name)}"
        if self._prompt_template_path:
            cmd += f" --prompt-file {shlex.quote(str(self._prompt_template_path))}"
        cmd += f" {shlex.quote(instruction)}"
        
        full_command = f"{export_cmd}{cmd}"

        commands.append(
            ExecInput(
                command=full_command,
                env=env,
            )
        )

        return commands"""
if b4 in text:
    text = text.replace(b4, r4)

# One edge case: delete the old create_cleanup_commands that was left.
text = text.replace("""    def create_cleanup_commands(self) -> list[ExecInput]:
        return [
            ExecInput(
                command=(
                    "find ~/.gemini/tmp -type f -name 'session-*.json' 2>/dev/null | "
                    "head -n 1 | xargs -r -I{} cp {} /logs/agent/gemini-cli.trajectory.json"
                ),
            ),
        ]""", "")

with open('src/harbor/agents/installed/gemini_cli.py', 'w') as f:
    f.write(text)
