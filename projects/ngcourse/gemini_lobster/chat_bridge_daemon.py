"""Daemon for bridging a Gemini CLI session to a Google Chat space.

This daemon runs a persistent Gemini CLI session in a PTY and polls
Google Chat for user input to relay to the CLI session.
"""

import argparse
import fcntl
import json
import logging
import os
import pty
import select
import shlex
import signal
import socket
import ssl
import struct
import subprocess
import sys
import termios
import threading
import time
import tty
from typing import List, Optional

from googleapiclient.errors import HttpError

try:
  from . import utils
except ImportError:
  import utils

POLL_INTERVAL = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


# ... (rest of imports)

class ChatDaemon:
  """Manages a Gemini CLI session bridged to Google Chat via One-Shot interactions."""

  def __init__(
      self,
      space_id: Optional[str],
      cmd_args: List[str],
      space_name: Optional[str] = None,
  ):
    self.service = utils.get_authenticated_service()
    self.cmd_args = cmd_args
    self.space_name = space_name
    self.last_message_time: Optional[str] = None
    self.stop_event = threading.Event()
    self.space_id = space_id or self.ensure_space()
    self.session_manager = utils.SessionManager()

  def ensure_space(self) -> str:
    """Ensures a destination Chat space exists, creating one if necessary."""
    try:
      cwd_path = os.getcwd().rstrip("/")
    except OSError:
      cwd_path = "/unknown"

    path_parts = cwd_path.split("/")
    cwd_name = path_parts[-1] or "Root"
    if cwd_name in ["google3", "googleplex-android"] and len(path_parts) > 1:
      cwd_name = path_parts[-2]

    known_spaces = {}
    if os.path.exists(utils.SPACES_CONFIG):
      try:
        with open(utils.SPACES_CONFIG, "r") as f:
          known_spaces = json.load(f)
      except (json.JSONDecodeError, IOError):
        pass

    # Check if we already have a space for this directory
    # Check if we already have a space for this directory
    if cwd_path != "/unknown" and cwd_path in known_spaces:
        existing_id = known_spaces[cwd_path]
        logger.info(f"Found configured Space {existing_id} for path {cwd_path}. Verifying...")
        try:
            self.service.spaces().get(name=existing_id).execute()
            logger.info(f"Verified Space {existing_id} exists.")
            return existing_id
        except Exception:
            logger.warning(f"Space {existing_id} is invalid or inaccessible. Creating a new one.")
            # Fall through to creation logic

    # Create new space
    display_name = f"🤖 {self.space_name}" if self.space_name else f"🤖 Gemini: {cwd_name}"
    
    logger.info("Creating new Space: %s...", display_name)
    body = {"space": {"display_name": display_name, "space_type": "SPACE"}}
    try:
        result = self.service.spaces().setup(body=body).execute()
        new_space_id = result["name"]
        
        # Set notifications to mentions only
        try:
            space_code = new_space_id.split("/")[-1]
            setting_name = f"users/me/spaces/{space_code}/spaceNotificationSetting"
            self.service.users().spaces().spaceNotificationSetting().patch(
                name=setting_name,
                body={"notification_setting": "FOR_YOU"},
                updateMask="notification_setting",
            ).execute()
        except Exception:
            logger.warning("Could not set notification settings")

        if cwd_path != "/unknown":
            known_spaces[cwd_path] = new_space_id
            os.makedirs(os.path.dirname(utils.SPACES_CONFIG), exist_ok=True)
            with open(utils.SPACES_CONFIG, "w") as f:
                json.dump(known_spaces, f)

        return new_space_id
    except Exception as e:
        logger.exception("Failed to ensure space")
        raise e

  def send_message(self, text: str, thread_id: str = None) -> None:
      """Sends a simple text message to the chat."""
      try:
          body = {"text": text}
          if thread_id:
              body["thread"] = {"name": thread_id}
          self.service.spaces().messages().create(
              parent=self.space_id, body=body
          ).execute()
      except Exception:
          logger.exception("Failed to send message")

  def run_one_shot(self, user_id: str, text: str, sender_name: str = None, thread_id: str = None) -> None:
      """Runs a one-shot Gemini CLI command with context."""
      # 1. Update Session History
      # We use the user_id as the session key to ensure dedicated per-user sessions
      session_key = user_id
      if not session_key:
          session_key = "default"
          
      session = self.session_manager.append_message(session_key, "user", text, sender_name=sender_name)
      
      # 2. Build Prompt
      t_start_prompt = time.time()
      full_prompt = self.session_manager.get_context_prompt(session_key, session=session)
      t_end_prompt = time.time()
      logger.info(f"Context prep (incl. summarization check) took {t_end_prompt - t_start_prompt:.2f}s")

      # 3. Indicator
      indicator_id = None
      try:
          msg = self.service.spaces().messages().create(
              parent=self.space_id,
              body={"text": "🔄 _Gemini is thinking..._"},
              threadKey=thread_id # threading?
          ).execute()
          indicator_id = msg["name"]
      except Exception:
          pass

      # 4. Run Command
      default_cmd = "/google/bin/releases/gemini-cli/tools/gemini"
      gemini_cmd_str = os.environ.get("GEMINI_COMMAND", default_cmd)
      if gemini_cmd_str == "gemini": gemini_cmd_str = default_cmd
      
      base_cmd = shlex.split(gemini_cmd_str)
      # Force non-interactive, YOLO mode, and pass prompt
      cmd = base_cmd + ["-y", "--prompt", full_prompt] + self.cmd_args
      
      logger.info("Running one-shot for %s", session_key)
      
      env = {
          **os.environ,
          "CHAT_BRIDGE_SPACE_ID": self.space_id,
          "CHAT_BRIDGE_THREAD_ID": thread_id or "",
          "CHAT_BRIDGE_USER_ID": user_id or "",
          "CHAT_BRIDGE_SILENT": "true", # Suppress hooks
      }

      try:
          # We purposefully capture stdout to get the final answer
          # But we also rely on the CLI to print the answer to stdout
          logger.info("Executing Gemini CLI: %s", " ".join(cmd))
          t_start_run = time.time()
          process = subprocess.run(cmd, capture_output=True, text=True, env=env)
          t_end_run = time.time()
          logger.info("Gemini CLI execution finished with exit code %s", process.returncode)
          logger.info(f"Gemini CLI execution took {t_end_run - t_start_run:.2f}s")
          
          output = process.stdout.strip()
          error_out = process.stderr.strip()
          
          # If output is empty but we have error, use error
          final_response = output if output else error_out
          
          # Clean up response (remove 'Output:' prefix if present from some internal formatting)
          # The utils.strip_reasoning might help too if it captures reasoning
          final_response = utils.strip_reasoning(final_response)
          
          # 5. Save Model Response
          if final_response:
              self.session_manager.append_message(session_key, "model", final_response)
              
              # 6. Send to Chat
              logger.info("Sending response to %s: %s...", session_key, final_response[:100])
              self.send_message(f"📦 {final_response}", thread_id=thread_id)
          else:
              self.send_message("⚠️ _No response from Gemini_", thread_id=thread_id)
              if error_out:
                  logger.error("Gemini Stderr: %s", error_out)

      except Exception as e:
          logger.exception("Failed to run gemini command")
          self.send_message(f"🚨 Error: {e}", thread_id=thread_id)
      finally:
          if indicator_id:
              try:
                  self.service.spaces().messages().delete(name=indicator_id).execute()
              except Exception:
                  pass

  def poll_loop(self) -> None:
      """Main polling loop."""
      logger.info("Chat Daemon started. Polling %s...", self.space_id)
      
      # Send initial greeting
      try:
          self.service.spaces().messages().create(
              parent=self.space_id,
              body={"text": f"\u200b🚀 *Session Started* (One-Shot Mode)\nHost: `{socket.gethostname()}`"}
          ).execute()
      except Exception:
          pass
          
      while not self.stop_event.is_set():
          time.sleep(POLL_INTERVAL)
          try:
              res = (
                  self.service.spaces()
                  .messages()
                  .list(parent=self.space_id, pageSize=20, orderBy="createTime desc")
                  .execute()
              )
              
              msgs = res.get("messages", [])

              # Initialize last_message_time on first run to avoid reprocessing old messages
              if self.last_message_time is None:
                  if msgs:
                      # msgs[0] is the latest because of 'orderBy=createTime desc'
                      self.last_message_time = msgs[0].get("createTime")
                  else:
                      self.last_message_time = "0"
                  logger.info("Initialized last_message_time to %s", self.last_message_time)
                  continue

              for msg in reversed(msgs):
                  create_time = msg.get("createTime")
                  if create_time <= self.last_message_time:
                      continue

                  self.last_message_time = create_time
                  text = msg.get("text", "").strip()
                  sender = msg.get("sender", {})
                  
                  # Filter bot's own messages
                  if sender.get("type") != "HUMAN":
                      continue
                      
                  # Check for mentions
                  is_mentioned = False
                  annotations = msg.get("annotations", [])
                  for ann in annotations:
                      if ann.get("type") == "USER_MENTION":
                          mention = ann.get("userMention", {})
                          user = mention.get("user", {})
                          # If the mentioned user is the bot itself (me)
                          if user.get("type") == "BOT":
                              is_mentioned = True
                              break
                  
                  # Check for fallback "@lobster" string if the user literal expects that
                  if "@lobster" in text.lower():
                      is_mentioned = True

                  if not is_mentioned:
                      continue

                  # Filter echos
                  if "\u200b" in text or text.startswith(("🚀", "🔄", "📦", "🚨", "⚠️")):
                      continue

                  logger.info("Processing message from %s: %s", sender.get("displayName"), text)
                  
                  if text.lower() == "/exit":
                      self.send_message("👋 Shutting down bridge.")
                      self.stop_event.set()
                      return
                  
                  # Run in thread to not block polling?
                  # For now, blocking is safer to avoid race conditions on session file, 
                  # unless we lock session file.
                  # Let's run synchronously for simplicity first.
                  thread_id = msg.get("thread", {}).get("name")
                  user_id = sender.get("name")
                  sender_name = sender.get("displayName")
                  
                  self.run_one_shot(user_id, text, sender_name=sender_name, thread_id=thread_id)

          except Exception:
              logger.exception("Poll loop error")
              time.sleep(5)

  def run(self) -> None:
      self.poll_loop()


def parse_args(argv: List[str]):
  """Manually parses arguments to extract space config while preserving others."""
  cmd_args = []
  space_name = None
  
  i = 0
  while i < len(argv):
    arg = argv[i]
    if arg == "--space-name":
      if i + 1 < len(argv):
        space_name = argv[i+1]
        i += 2
        continue
    elif arg.startswith("--space-name="):
      space_name = arg.split("=", 1)[1]
      i += 1
      continue
    
    cmd_args.append(arg)
    i += 1

  space_id = None
  # Check if the first argument is a space ID (heuristic: starts with spaces/)
  if cmd_args and cmd_args[0].startswith("spaces/"):
    space_id = cmd_args[0]
    cmd_args = cmd_args[1:]
  else:
    space_id = os.environ.get("SPACE_ID")

  return space_id, cmd_args, space_name


def main():
  space_id, cmd_args, space_name = parse_args(sys.argv[1:])
  ChatDaemon(space_id, cmd_args, space_name=space_name).run()


if __name__ == "__main__":
  main()
