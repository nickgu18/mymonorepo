"""Gemini CLI transport implementation."""

import logging
import os
import shutil
from collections.abc import AsyncIterator
from contextlib import suppress
from subprocess import PIPE
from typing import Any

import anyio
import anyio.abc
from anyio.abc import Process
from anyio.streams.text import TextReceiveStream

from ..._errors import CLIConnectionError, CLINotFoundError, ProcessError
from ...types import ClaudeAgentOptions
from . import Transport

logger = logging.getLogger(__name__)

class GeminiCLITransport(Transport):
    """Transport for Gemini CLI."""

    def __init__(
        self,
        prompt: str,
        options: ClaudeAgentOptions,
    ):
        self._prompt = prompt
        self._options = options
        self._cli_path = (
            str(options.cli_path) if options.cli_path is not None else self._find_cli()
        )
        self._cwd = str(options.cwd) if options.cwd else None
        self._process: Process | None = None
        self._stdout_stream: TextReceiveStream | None = None
        self._ready = False
        self._exit_error: Exception | None = None

    def _find_cli(self) -> str:
        """Find Gemini CLI binary."""
        if cli := shutil.which("gemini"):
            return cli
        
        # Fallback locations? For now just rely on PATH
        raise CLINotFoundError("Gemini CLI not found. Please install it.")

    async def connect(self) -> None:
        """Start gemini process."""
        if self._process:
            return

        # Build command: gemini -y -p "prompt" --output-format stream-json
        # NOTE: We might need to support options like --model etc via options.extra_args
        cmd = [self._cli_path, "-y", "-p", self._prompt, "--output-format", "stream-json"]
        
        # Add basic options
        if self._options.model:
            cmd.extend(["--model", self._options.model])
        
        # Add any extra args
        for flag, value in self._options.extra_args.items():
            if value is None:
                cmd.append(f"--{flag}")
            else:
                cmd.extend([f"--{flag}", str(value)])

        try:
             self._process = await anyio.open_process(
                cmd,
                stdin=PIPE, # We might not need stdin if it's one-shot, but open just in case
                stdout=PIPE,
                stderr=PIPE, # We usually want to see stderr
                cwd=self._cwd,
                env=os.environ, # Pass through env
            )
             
             if self._process.stdout:
                 self._stdout_stream = TextReceiveStream(self._process.stdout)
            
             if self._process.stderr:
                 self._stderr_stream = TextReceiveStream(self._process.stderr)
                 # Start a task to read stderr
                 self._stderr_tg = anyio.create_task_group()
                 await self._stderr_tg.__aenter__()
                 self._stderr_tg.start_soon(self._read_stderr)

             self._ready = True

        except Exception as e:
            error = CLIConnectionError(f"Failed to start Gemini CLI: {e}")
            self._exit_error = error
            raise error from e

    async def _read_stderr(self) -> None:
        """Read stderr."""
        if not self._stderr_stream:
            return
        
        try:
            async for line in self._stderr_stream:
                line = line.strip()
                if line:
                    logger.debug(f"Gemini stderr: {line}")
                    if self._options.stderr:
                         self._options.stderr(line)
        except Exception:
            pass

    async def close(self) -> None:
        if hasattr(self, "_stderr_tg") and self._stderr_tg:
            with suppress(Exception):
                self._stderr_tg.cancel_scope.cancel()
                await self._stderr_tg.__aexit__(None, None, None)
        
        if self._process:
            with suppress(Exception):
                self._process.terminate()
            self._process = None
        self._ready = False

    async def write(self, data: str) -> None:
        """Write to stdin - Gemini CLI might not support interactive input in this mode."""
        # For now, we assume one-shot. If we need interaction, we might need a different mode.
        pass

    def read_messages(self) -> AsyncIterator[dict[str, Any]]:
        """Read messages from stdout."""
        # Reuse SubprocessCLITransport logic specifically for JSON reading if possible, 
        # but here we'll just implement a simple reader since we can't easily inherit 
        # (SubprocessCLITransport has a lot of Claude specific stuff).
        # Actually, maybe we should abstract `read_messages` JSON parsing into a mixin or utility.
        # For now, I'll copy the JSON reading logic.
        return self._read_messages_impl()

    async def _read_messages_impl(self) -> AsyncIterator[dict[str, Any]]:
        if not self._process or not self._stdout_stream:
            raise CLIConnectionError("Not connected")
            
        import json
        
        try:
            async for line in self._stdout_stream:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    
                    # Adapter for Gemini -> Claude protocol
                    msg_type = data.get("type")
                    
                    if msg_type == "message":
                        role = data.get("role")
                        content = data.get("content")
                        # Transform to {"type": role, "message": {"role": role, "content": content}}
                        if role in ["user", "assistant"]:
                            data = {
                                "type": role,
                                "message": {
                                    "role": role,
                                    "content": content,
                                    "model": data.get("model", "gemini"), # assistant needs model
                                }
                            }
                            # Handle delta for streaming?
                            if "delta" in data and data["delta"]:
                                # StreamEvent? No, parse_message handles StreamEvent differently
                                # If it's partial, Claude uses "stream_event"?
                                # Gemini output {"type":"message", ..., "delta":true}
                                # We might need to map to "stream_event" if we want streaming.
                                # But for now let's try mapping to normal message if it's complete?
                                # Actually "delta": true implies streaming chunks.
                                # parse_message for 'assistant' expects FULL message content usually?
                                # Logic in parse_message for 'assistant':
                                #   content_blocks = [] ... for block in data["message"]["content"] ...
                                # It expects content to be list of blocks?
                                # Gemini content is string "Hello! How".
                                # We should wrap it in TextBlock?
                                # content=[{"type": "text", "text": content}]
                                if isinstance(content, str):
                                    data["message"]["content"] = [{"type": "text", "text": content}]
                                pass

                    elif msg_type == "result":
                        # Adapt result
                        # Gemini: {"type":"result", "status":"success", "stats":{...}}
                        # Claude: {"type":"result", "subtype": "success", ...}
                        if "subtype" not in data and "status" in data:
                            data["subtype"] = data["status"]
                        
                        # Populate required fields if missing
                        if "duration_ms" not in data:
                            data["duration_ms"] = data.get("stats", {}).get("duration_ms", 0)
                        if "duration_api_ms" not in data:
                            data["duration_api_ms"] = 0
                        if "is_error" not in data:
                            data["is_error"] = data["status"] != "success"
                        if "num_turns" not in data:
                            data["num_turns"] = 1 # One-shot
                        if "session_id" not in data:
                            data["session_id"] = "unknown"
                    
                    elif msg_type == "init":
                         # Ignore init
                         continue
                         
                    # Yield adapted data
                    yield data
                    
                except json.JSONDecodeError as e:
                    # Log invalid JSON if needed
                    logger.warning(f"Invalid JSON from Gemini CLI: {line[:100]}... Error: {e}")
                    # If it's not JSON, maybe it's just text? 
                    # For now, we yield it as a text chunk if it looks like text?
                    # But the protocol expects dict. 
                    pass
        except anyio.ClosedResourceError:
            pass
        
        # Wait for process
        returncode = await self._process.wait()
        
        if returncode != 0:
            stderr = ""
            if self._process.stderr:
                # We need to read stderr if we haven't already. 
                # But we piped it. 
                # If we didn't consume it, it might fill up buffer? 
                # anyio open_process with PIPE for stderr but no reader might deadlock if stderr is huge.
                # But here we just check it at the end.
                # We can't easily read it now if it was piped and not consumed?
                # actually check SubprocessCLITransport to see how it handles stderr.
                pass
            
            raise ProcessError(
                f"Gemini CLI failed with exit code {returncode}",
                exit_code=returncode,
                stderr=stderr,
            )

    async def close(self) -> None:
        if self._process:
            with suppress(Exception):
                self._process.terminate()
            self._process = None
        self._ready = False

    def is_ready(self) -> bool:
        return self._ready

    async def end_input(self) -> None:
        pass
