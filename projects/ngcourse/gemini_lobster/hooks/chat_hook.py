"""Hook script for relaying Gemini CLI events to Google Chat."""

import argparse
import json
import logging
import os
import re
import sys
import time
from typing import Optional
from googleapiclient.errors import HttpError

try:
  from .. import utils  # pylint: disable=g-import-not-at-top
except (ImportError, ValueError):
  import utils  # pylint: disable=g-import-not-at-top


logger = logging.getLogger(__name__)


def truncate_output(text: str, max_lines: int = 5) -> str:
  """Truncates text to the last max_lines if it exceeds the limit."""
  if not text:
    return ""
  lines = text.splitlines()
  if len(lines) > max_lines:
    truncated = lines[-max_lines:]
    return (
        f"... ({len(lines) - max_lines} lines truncated) ...\n"
        + "\n".join(truncated)
    )
  return text


def format_tool_start(tool_name: str, tool_input: dict) -> str:
  """Formats tool start message to be concise and mobile-friendly."""
  command = tool_input.get("command")
  description = tool_input.get("description")
  instruction = tool_input.get("instruction")
  file_path = tool_input.get("file_path") or tool_input.get("filename")

  # Special handling for common tools
  if tool_name == "run_shell_command":
    if command:
      return f"💻 `{command}`"
    return "💻 Shell Command"

  if tool_name == "replace":
    msg = "📝 **Edit**"
    if file_path:
      msg += f" `{os.path.basename(file_path)}`"
    if instruction:
      msg += f": {instruction}"
    return msg

  if tool_name == "write_file":
    msg = "💾 **Write**"
    if file_path:
      msg += f" `{os.path.basename(file_path)}`"
    return msg

  if tool_name == "read_file":
    msg = "📄 **Read**"
    if file_path:
      msg += f" `{os.path.basename(file_path)}`"
    return msg

  # Generic fallback
  # Prefer instruction > description > tool_name
  # But ignore description if it looks like a docstring (long)
  main_text = instruction
  if not main_text:
    if description and len(description) < 60:
      main_text = description
    else:
      main_text = tool_name

  content = f"🔨 {main_text}"

  # Add significant args for generic tools, excluding verbose ones
  ignored_args = {
      "command",
      "description",
      "instruction",
      "content",
      "old_string",
      "new_string",
      "source_code",
  }
  other_args = {k: v for k, v in tool_input.items() if k not in ignored_args}

  if other_args:
    args_parts = []
    for k, v in other_args.items():
      val_str = str(v)
      if len(val_str) > 50:
        val_str = val_str[:47] + "..."
      args_parts.append(f"{k}='{val_str}'")
    content += f" ({', '.join(args_parts)})"

  if command:
    content += f"\n💻 `{command}`"

  return content


def send_to_chat(
    service,
    space_id: str,
    thread_id: Optional[str],
    text: str,
    message_id: str,
    mention_user_id: Optional[str] = None,
) -> bool:
  """Sends a message to a Google Chat space with deduplication and optional mention."""

  # Special handling for already prefixed text
  prefix = ""
  if text.startswith(("🛠️", "📝", "👤", "🚀", "✦", "📦", "💻", "🚨", "⚠️", "ℹ️")):
    prefix = text[0:2]  # Emoji + space or just emoji
    if prefix.strip() in [
        "🛠️",
        "📝",
        "👤",
        "🚀",
        "✦",
        "📦",
        "💻",
        "🚨",
        "⚠️",
        "ℹ️",
    ]:
      inner_text = text[2:].strip()
    else:
      prefix = ""
      inner_text = text.strip()
  else:
    inner_text = text.strip()

  clean_inner = utils.clean_text(inner_text)

  if not clean_inner and not prefix:
    return False

  runtime_data = utils.load_runtime_data()
  sent_ids = runtime_data.get("sent_ids", [])
  if message_id in sent_ids:
    return False

  sent_ids.append(message_id)

  runtime_data["sent_ids"] = sent_ids[-100:]
  utils.save_runtime_data(runtime_data)

  # Apply formatting
  if prefix:
    if clean_inner:
      if "```" in clean_inner:
        formatted_text = f"{prefix} {clean_inner}"
      elif "\n" in clean_inner:
        formatted_text = f"{prefix} \n```\n{clean_inner}\n```"
      else:
        formatted_text = f"{prefix} {clean_inner}"
    else:
      formatted_text = prefix  # Just the emoji (e.g. 📦 for empty tool output)
  else:
    if "```" in clean_inner:
      formatted_text = clean_inner
    else:
      formatted_text = (
          f"```\n{clean_inner}\n```"
          if "\n" in clean_inner
          else f"✦ {clean_inner}"
      )

  # Add mention if requested
  if mention_user_id:
    formatted_text += f" <{mention_user_id}>"

  body = {"text": f"\u200b{formatted_text}"}
  if thread_id:
    body["thread"] = {"name": thread_id}

  if len(body["text"]) > 4000:
    body["text"] = body["text"][:3997] + "..."

  for attempt in range(4):  # Try 4 times (initial + 3 retries)
    try:
      service.spaces().messages().create(parent=space_id, body=body).execute()
      return True
    except HttpError as e:
      if e.resp.status == 429 or e.resp.status >= 500:
        if attempt < 3:
          sleep_time = (2**attempt) + (0.1 * (time.time() % 1))  # Jitter
          time.sleep(sleep_time)
          continue
      logger.exception("Error sending to chat (HttpError)")
      return False
    except Exception:
      logger.exception("Error sending to chat")
      return False
  return False


def main() -> None:
  """Main entry point for the hook script."""
  log_path = os.path.join(utils.DATA_DIR, "hook.log")
  os.makedirs(utils.DATA_DIR, exist_ok=True)
  logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(message)s",
      handlers=[logging.FileHandler(log_path)],
  )

  parser = argparse.ArgumentParser()
  parser.add_argument("--event", required=True)
  args = parser.parse_args()

  # Attempt to read input first
  try:
    raw_input = sys.stdin.read()
    input_data = json.loads(raw_input) if raw_input else {}
  except Exception:
    input_data = {}

  runtime_data = utils.load_runtime_data()

  space_id = os.environ.get("CHAT_BRIDGE_SPACE_ID") or runtime_data.get(
      "space_id"
  )
  thread_id = os.environ.get("CHAT_BRIDGE_THREAD_ID") or runtime_data.get(
      "thread_id"
  )
  user_id = os.environ.get("CHAT_BRIDGE_USER_ID") or runtime_data.get("user_id")
  sent_from_chat = runtime_data.get("sent_from_chat", [])
  sent_ids = runtime_data.get("sent_ids", [])

  # If silent mode is on, suppress most outputs
  if os.environ.get("CHAT_BRIDGE_SILENT") == "true":
    if args.event not in ["error", "failure"]:
      # We might still want to capture error events, but suppress tools/thinking
      print(json.dumps({"decision": "allow", "suppressOutput": True}))
      return

  if not space_id:
    print(json.dumps({"decision": "allow", "suppressOutput": True}))
    return

  try:
    service = utils.get_authenticated_service()

    if args.event == "tool_start":
      tool_name = input_data.get("tool_name", "Tool")
      tool_input = input_data.get("tool_input", {})
      content = format_tool_start(tool_name, tool_input)

      if content:
        timestamp = input_data.get("timestamp", str(time.time()))
        call_id = f"tool_start_{tool_name}_{timestamp}"
        if send_to_chat(service, space_id, thread_id, content, call_id):
          sent_ids.append(call_id)

    elif args.event == "tool_output":
      tool_name = input_data.get("tool_name", "Tool")
      tool_response = input_data.get("tool_response", {})

      if tool_response:
        output_text = ""
        if isinstance(tool_response, dict) and tool_response.get("error"):
          error_obj = tool_response["error"]
          error_msg = (
              error_obj.get("message")
              if isinstance(error_obj, dict)
              else str(error_obj)
          )
          output_text = f"🚨 {error_msg}"
        elif isinstance(tool_response, dict) and tool_response.get(
            "returnDisplay"
        ):
          disp = tool_response["returnDisplay"]
          if isinstance(disp, str):
            output_text = disp
          elif isinstance(disp, dict) and "fileDiff" in disp:
            output_text = (
                "📝 Edit"
                f" {disp.get('fileName', 'file')}:\n{disp.get('fileDiff', '')}"
            )
          else:
            output_text = str(disp)
        elif isinstance(tool_response, dict) and tool_response.get(
            "llmContent"
        ):
          content = tool_response["llmContent"]
          if isinstance(content, str):
            if "Command:" in content and "Output:" in content:
              match = re.search(
                  r"Output: (.*?)(?:\n(Error|Exit Code):|$)", content, re.DOTALL
              )
              output_text = match.group(1).strip() if match else content
            else:
              output_text = content
          else:
            output_text = str(content)
        elif isinstance(tool_response, dict):
          if "output" in tool_response:
            output_text = str(tool_response["output"])
          elif "stdout" in tool_response:
            output_text = str(tool_response["stdout"])
          else:
            output_text = json.dumps(tool_response, indent=2)
        else:
          output_text = str(tool_response)

        timestamp = input_data.get("timestamp", str(time.time()))
        result_id = f"tool_output_{tool_name}_{timestamp}"
        output_text = truncate_output(output_text)

        if send_to_chat(
            service, space_id, thread_id, f"📦 {output_text}", result_id
        ):
          sent_ids.append(result_id)

    elif args.event == "error":
      error_data = input_data.get("error")
      if error_data:
        error_msg = (
            error_data.get("message")
            if isinstance(error_data, dict)
            else str(error_data)
        )
        timestamp = input_data.get("timestamp", str(time.time()))
        error_id = f"error_{timestamp}"
        if send_to_chat(
            service,
            space_id,
            thread_id,
            f"🚨 {error_msg}",
            error_id,
            mention_user_id=user_id,
        ):
          sent_ids.append(error_id)

    transcript_path = input_data.get("transcript_path")
    if transcript_path and os.path.exists(transcript_path):
      with open(transcript_path, "r") as f:
        transcript = json.load(f)
        messages = transcript.get("messages", [])

      for i, msg in enumerate(messages[-5:]):
        msg_id = msg.get("id")
        msg_type = msg.get("type")
        msg_content = (msg.get("content") or "").strip()

        if not msg_id or (
            not msg_content and msg_type not in ("tool", "gemini", "model")
        ):
          continue

        if msg_type == "user":
          if msg_content not in sent_from_chat:
            send_to_chat(
                service,
                space_id,
                thread_id,
                f"👤 {msg_content}",
                f"echo_{msg_id}",
            )

        elif msg_type == "error":
          send_to_chat(
              service,
              space_id,
              thread_id,
              f"🚨 {msg_content}",
              msg_id,
              mention_user_id=user_id,
          )

        elif msg_type == "warning":
          send_to_chat(service, space_id, thread_id, f"⚠️ {msg_content}", msg_id)

        elif msg_type == "info":
          send_to_chat(service, space_id, thread_id, f"ℹ️ {msg_content}", msg_id)

        elif msg_type == "tool":
          send_to_chat(
              service,
              space_id,
              thread_id,
              f"📦 {truncate_output(msg_content)}",
              msg_id,
          )

        elif msg_type in ("gemini", "model"):
          tool_calls = msg.get("toolCalls", [])
          for tc in tool_calls:
            tc_id = tc.get("id")
            if not tc_id:
              continue

            call_id = f"{tc_id}_call"
            if call_id not in sent_ids:
              name = tc.get("displayName", tc.get("name", "Tool"))
              tool_args = tc.get("args", {})
              content = format_tool_start(name, tool_args)
              if send_to_chat(service, space_id, thread_id, content, call_id):
                sent_ids.append(call_id)

            result_text = tc.get("resultDisplay")
            if result_text:
              if not isinstance(result_text, str):
                if isinstance(result_text, dict) and "fileDiff" in result_text:
                  result_text = (
                      "📝 Edit"
                      f" {result_text.get('fileName', 'file')}:\n{result_text.get('fileDiff', '')}"
                  )
                else:
                  result_text = str(result_text)

            if not result_text:
              result = tc.get("result")
              if result:
                if isinstance(result, list):
                  parts_text = []
                  for p in result:
                    if isinstance(p, dict):
                      if "text" in p:
                        parts_text.append(p["text"])
                      elif "functionResponse" in p:
                        parts_text.append(
                            str(
                                p["functionResponse"]
                                .get("response", {})
                                .get("output", "")
                            )
                        )
                      else:
                        parts_text.append(str(p))
                    else:
                      parts_text.append(str(p))
                  result_text = "\n".join(parts_text)
                else:
                  result_text = str(result)

            if result_text:
              result_id = f"{tc_id}_result"
              if result_id not in sent_ids:
                if send_to_chat(
                    service,
                    space_id,
                    thread_id,
                    f"📦 {truncate_output(result_text)}",
                    result_id,
                ):
                  sent_ids.append(result_id)

          clean_content = utils.strip_reasoning(msg_content)

          if clean_content:
            send_to_chat(
                service,
                space_id,
                thread_id,
                clean_content,
                msg_id,
            )

  except Exception:
    logger.exception("Global hook error")

  print(json.dumps({"decision": "allow", "suppressOutput": True}))


if __name__ == "__main__":
  main()
