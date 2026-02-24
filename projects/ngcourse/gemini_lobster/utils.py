"""Shared utilities for Gemini Chat Bridge."""

# CRITICAL: Prevent shadowing of standard library modules by google3 root
# We move all 'site-packages' and '/usr/lib' paths to the front.
import sys
import os
stdlib_paths = [p for p in sys.path if "site-packages" in p or p.startswith("/usr/lib")]
for p in reversed(stdlib_paths):
    if p in sys.path:
        sys.path.remove(p)
        sys.path.insert(0, p)

import hashlib
import json
import logging
import re
import time
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/chat.messages",
    "https://www.googleapis.com/auth/chat.spaces",
    "https://www.googleapis.com/auth/chat.users.spacesettings",
]

DATA_DIR = os.path.expanduser("~/.gemini_chat_bridge")
RUNTIME_CONFIG = os.path.expanduser("~/.gemini/chat_bridge_runtime.json")
SPACES_CONFIG = os.path.expanduser("~/.gemini/chat_bridge_spaces.json")


def get_authenticated_service():
    """Authenticates with Google APIs and returns a Chat service object."""
    creds = None
    token_path = os.path.join(DATA_DIR, "token.json")
    creds_path = os.path.join(DATA_DIR, "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Credentials not found at {creds_path}")
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_path, SCOPES, redirect_uri="http://localhost"
            )
            auth_url, _ = flow.authorization_url(prompt="consent")
            print(f"Authorize here: {auth_url}\n")
            code = input("Enter code: ").strip()
            flow.fetch_token(code=code)
            creds = flow.credentials

        os.makedirs(os.path.dirname(token_path), exist_ok=True)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("chat", "v1", credentials=creds, cache_discovery=False)


def clean_text(text: str, strip_markdown: bool = False) -> str:
  """Removes ANSI escape sequences, UI clutter, and optionally markdown."""

  if not text:
    return ""

  # Remove ANSI escape sequences
  text = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", text)
  text = re.sub(r"\x1b\][0-9;]*\x07", "", text)
  text = re.sub(r"\x1b\([AB012]", "", text)

  # Remove UI box characters and spinners
  box_chars = r"[╭╮╯╰─│┌┐└┘├┤┬┴┼═║╒╓╔╕╖╗╘╙╚╛╜╝╞╟╠╡╢╣╤╥╦╧╨╩╪╫╬█■]"
  text = re.sub(box_chars, "", text)
  text = re.sub(r"[⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏]", "", text)

  # Remove "screen reader" nag
  text = re.sub(
      r"You are currently in screen reader-friendly view.*?next run\.",
      "",
      text,
      flags=re.DOTALL | re.IGNORECASE,
  )

  if strip_markdown:
    text = re.sub(r"[*_`]", "", text)

  # Patterns for Gemini CLI UI elements to filter out
  ui_patterns = [
      r"Prioritizing.*Response",
      r"Clarifying.*Response",
      r".*context file.*YOLO mode",
      r"^\*\s+Type your message",
      r"~\s+no sandbox",
      r"gemini-.* /model",
  ]

  lines = []
  for line in text.splitlines():
    clean_line = line.strip()
    if not clean_line or clean_line == ">":
      continue

    # Skip lines that match UI patterns
    if any(re.search(p, clean_line) for p in ui_patterns):
      continue

    lines.append(clean_line)
  return "\n".join(lines)


def strip_reasoning(text: str) -> str:
    """Heuristic to strip reasoning/thinking from model responses."""
    if not text:
        return ""

    # If the text has a ✦, the CLI has already formatted it. Extract the answer.
    if "✦" in text:
        return text.split("✦", 1)[1].strip()

    # Fallback: Just return the text as-is.
    # The previous heuristic (len(parts) > 2) was too aggressive for chat.
    return text.strip()


def get_content_id(content: str) -> str:
    """Generates a stable, content-based ID for deduplication."""
    if not content:
        return "empty"
    return hashlib.md5(content.strip().encode("utf-8")).hexdigest()[:12]


def load_runtime_data() -> dict:
    """Loads runtime configuration data."""
    if os.path.exists(RUNTIME_CONFIG):
        try:
            with open(RUNTIME_CONFIG, "r") as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
    return {}


def save_runtime_data(data: dict) -> None:
    """Saves runtime configuration data."""
    os.makedirs(os.path.dirname(RUNTIME_CONFIG), exist_ok=True)
    try:
        with open(RUNTIME_CONFIG, "w") as f:
            json.dump(data, f)
    except IOError:
        logging.getLogger(__name__).error("Failed to save runtime data")


class SessionManager:
    """Manages chat sessions stored in JSON files."""

    def __init__(self, sessions_dir: str = None):
        if sessions_dir:
            self.sessions_dir = sessions_dir
        else:
            self.sessions_dir = os.path.join(DATA_DIR, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)

    def _get_session_path(self, session_id: str) -> str:
        # Sanitize session_id to be safe for filenames
        safe_id = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", session_id)
        return os.path.join(self.sessions_dir, f"{safe_id}.json")

    def load_session(self, session_id: str, sender_name: str = None) -> dict:
        """Loads a session by ID, returning a default structure if new."""
        path = self._get_session_path(session_id)
        session = None
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    session = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        if not session:
            session = {
                "session_id": session_id,
                "user_name": sender_name,
                "messages": [],
                "summary": None,
                "created_at": str(time.time()),
                "last_updated": str(time.time()),
            }
        elif sender_name and session.get("user_name") != sender_name:
            session["user_name"] = sender_name

        return session

    def save_session(self, session_id: str, data: dict) -> None:
        """Saves a session to disk."""
        path = self._get_session_path(session_id)
        data["last_updated"] = str(time.time())
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
        except IOError:
            logging.getLogger(__name__).error(f"Failed to save session {session_id}")

    def append_message(self, session_id: str, role: str, content: str, sender_name: str = None) -> dict:
        """Appends a message to the session and saves it."""
        session = self.load_session(session_id, sender_name)
        session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": str(time.time())
        })
        
        # If we hit 20 turns, summarize and reset
        if len(session["messages"]) >= 20:
             return self.summarize_session(session_id, session)
        
        self.save_session(session_id, session)
        return session

    def summarize_session(self, session_id: str, session: dict) -> dict:
        """Summarizes the session and resets the message history."""
        logging.getLogger(__name__).info(f"Summarizing session {session_id}...")
        t_start_summ = time.time()
        
        context = self.get_context_prompt(session_id, session)
        prompt = (
            f"Please provide a concise summary of the following conversation with {session.get('user_name', 'a user')}. "
            "Focus on key facts, decisions, and current state. This summary will be used as the new 'starting point' "
            "for the AI assistant.\n\n"
            f"{context}\n\nSummary:"
        )

        default_cmd = "/google/bin/releases/gemini-cli/tools/gemini"
        gemini_cmd_str = os.environ.get("GEMINI_COMMAND", default_cmd)
        if gemini_cmd_str == "gemini": gemini_cmd_str = default_cmd
        
        import shlex
        import subprocess
        # Use simple args, ensure silent mode for hooks if possible via env
        cmd = shlex.split(gemini_cmd_str) + ["-y", "--prompt", prompt]
        env = os.environ.copy()
        env["CHAT_BRIDGE_SILENT"] = "true"
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
            summary = result.stdout.strip()
            if summary:
                session["summary"] = summary
                session["messages"] = [] # Reset history
                logging.getLogger(__name__).info("Session summarized.")
        except Exception:
            logging.getLogger(__name__).error(f"Summarization failed for {session_id}")

        t_end_summ = time.time()
        logging.getLogger(__name__).info(f"Session summarization took {t_end_summ - t_start_summ:.2f}s")
        self.save_session(session_id, session)
        return session
    
    def get_context_prompt(self, session_id: str, session: dict = None) -> str:
        """Constructs a prompt with summary + history."""
        if session is None:
            session = self.load_session(session_id)
            
        messages = session.get("messages", [])
        summary = session.get("summary")
        user_name = session.get("user_name", "User")
        
        context_parts = []
        if summary:
            context_parts.append(f"PREVIOUS CONTEXT SUMMARY:\n{summary}\n")

        if messages:
            context_parts.append("CONVERSATION HISTORY:")
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "").strip()
                if not content: continue
                
                label = user_name if role == "user" else "GEMINI"
                context_parts.append(f"{label}: {content}")
        
        return "\n".join(context_parts)
