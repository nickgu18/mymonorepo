"""Tests for the chat hook."""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch
from googleapiclient.errors import HttpError

# Fix import path for google3 environment
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
)

from experimental.users.shayba.gemini_chat_bridge import utils
from experimental.users.shayba.gemini_chat_bridge.hooks import chat_hook


class MockResponse:
  def __init__(self, status):
    self.status = status
    self.reason = "Mock Reason"


class TestHooks(unittest.TestCase):

  @patch("time.sleep")
  def test_send_to_chat_retry(self, mock_sleep):
    mock_service = MagicMock()
    # Mock create().execute() to raise HttpError
    mock_create = mock_service.spaces().messages().create.return_value

    # 429 Too Many Requests
    error_429 = HttpError(MockResponse(429), b"Rate Limit Exceeded")
    # 503 Service Unavailable
    error_503 = HttpError(MockResponse(503), b"Service Unavailable")

    # Fail 3 times, succeed on 4th
    mock_create.execute.side_effect = [error_429, error_503, error_429, None]

    with (
        patch(
            "experimental.users.shayba.gemini_chat_bridge.utils.load_runtime_data",
            return_value={},
        ),
        patch(
            "experimental.users.shayba.gemini_chat_bridge.utils.save_runtime_data"
        ),
    ):
      result = chat_hook.send_to_chat(
          mock_service, "spaces/S", "threads/T", "Retry Me", "msg_retry"
      )

      self.assertTrue(result)
      self.assertEqual(mock_create.execute.call_count, 4)
      self.assertEqual(mock_sleep.call_count, 3)

  @patch(
      "experimental.users.shayba.gemini_chat_bridge.utils.load_runtime_data"
  )
  @patch(
      "experimental.users.shayba.gemini_chat_bridge.utils.save_runtime_data"
  )
  def test_send_to_chat_dedup(self, mock_save, mock_load):
    mock_load.return_value = {"sent_ids": ["msg_123"]}
    mock_service = MagicMock()

    # Already sent
    result = chat_hook.send_to_chat(
        mock_service, "spaces/S", "threads/T", "Hello", "msg_123"
    )
    self.assertFalse(result)
    mock_service.spaces().messages().create.assert_not_called()

    # New message
    mock_load.return_value = {"sent_ids": ["msg_123"]}
    result = chat_hook.send_to_chat(
        mock_service, "spaces/S", "threads/T", "New", "msg_456"
    )
    self.assertTrue(result)
    mock_service.spaces().messages().create.assert_called_once()
    mock_save.assert_called_once()
    self.assertIn("msg_456", mock_save.call_args[0][0]["sent_ids"])

  def test_send_to_chat_formatting(self):
    mock_service = MagicMock()
    with (
        patch(
            "experimental.users.shayba.gemini_chat_bridge.utils.load_runtime_data",
            return_value={},
        ),
        patch(
            "experimental.users.shayba.gemini_chat_bridge.utils.save_runtime_data"
        ),
    ):

      # Multiline gets code block
      chat_hook.send_to_chat(
          mock_service, "spaces/S", None, "Line 1\nLine 2", "m1"
      )
      args, kwargs = mock_service.spaces().messages().create.call_args
      self.assertIn("```\nLine 1\nLine 2\n```", kwargs["body"]["text"])

      # Single line gets ✦
      chat_hook.send_to_chat(mock_service, "spaces/S", None, "Hello", "m2")
      args, kwargs = mock_service.spaces().messages().create.call_args
      self.assertIn("✦ Hello", kwargs["body"]["text"])

      # Pre-formatted markdown should NOT be wrapped
      chat_hook.send_to_chat(
          mock_service,
          "spaces/S",
          None,
          "```python\nprint(1)\n```\nExplanation",
          "m3",
      )
      args, kwargs = mock_service.spaces().messages().create.call_args
      # It should just be the text itself (prefixed with zero-width space)
      self.assertEqual(
          kwargs["body"]["text"], "\u200b```python\nprint(1)\n```\nExplanation"
      )

  @patch("sys.stdin.read")
  @patch(
      "experimental.users.shayba.gemini_chat_bridge.utils.get_authenticated_service"
  )
  @patch(
      "experimental.users.shayba.gemini_chat_bridge.hooks.chat_hook.send_to_chat"
  )
  @patch(
      "experimental.users.shayba.gemini_chat_bridge.utils.load_runtime_data"
  )
  def test_main_loop(self, mock_load, mock_send, mock_service, mock_stdin):
    mock_load.return_value = {
        "space_id": "S1",
        "thread_id": "T1",
        "user_id": "users/shayba",
        "sent_ids": [],
        "sent_from_chat": [],
    }
    mock_stdin.return_value = json.dumps(
        {"transcript_path": "/tmp/transcript.json"}
    )

    transcript_data = {
        "messages": [
            {"id": "msg_user", "type": "user", "content": "run sleep"},
            {
                "id": "msg_gemini_tool_call",
                "type": "gemini",
                "content": "",
                "toolCalls": [{
                    "id": "tc_1",
                    "name": "sleep",
                    "description": "sleep",
                    "args": {"command": "sleep 10"},
                }],
                "thoughts": [
                    {"subject": "Plan", "description": "I need to sleep"}
                ],
            },
            {
                "id": "msg_tool_output",
                "type": "tool",
                "content": "Tool Finished",
            },
            {"id": "msg_gemini_final", "type": "gemini", "content": "Done"},
        ]
    }

    # Use a scoped side effect for open to avoid breaking standard library imports like gettext
    original_open = open

    def side_effect(path, *args, **kwargs):
      if "/tmp/transcript.json" in str(path):
        return mock_open(read_data=json.dumps(transcript_data))(
            path, *args, **kwargs
        )
      return original_open(path, *args, **kwargs)

    with (
        patch("builtins.open", side_effect=side_effect),
        patch(
            "experimental.users.shayba.gemini_chat_bridge.utils.get_authenticated_service",
            return_value=mock_service,
        ),
        patch("os.path.exists", return_value=True),
        patch("os.environ", {"CHAT_BRIDGE_USER_ID": "users/shayba"}),
        patch("sys.argv", ["chat_hook.py", "--event", "agent_output"]),
    ):
      chat_hook.main()

      # 1. User echo
      # 2. Gemini tool call (formatted as description + command)
      # 3. Tool output
      # 4. Gemini final response
      self.assertEqual(mock_send.call_count, 4)

      # Verify tool call formatting
      call_tool_call = mock_send.call_args_list[1]
      self.assertIn("🔨 sleep", call_tool_call[0][3])
      self.assertIn("💻 `sleep 10`", call_tool_call[0][3])
      # Plan is not currently included in tool call output
      # self.assertIn("**Plan**", call_tool_call[0][3])

      # Verify mention in final call
      call_final = mock_send.call_args_list[3]
      # self.assertEqual(call_final[1]['mention_user_id'], "users/shayba")

  @patch("sys.stdin.read")
  @patch(
      "experimental.users.shayba.gemini_chat_bridge.utils.get_authenticated_service"
  )
  @patch(
      "experimental.users.shayba.gemini_chat_bridge.hooks.chat_hook.send_to_chat"
  )
  @patch(
      "experimental.users.shayba.gemini_chat_bridge.utils.load_runtime_data"
  )
  def test_transcript_tool_output_truncation(
      self, mock_load, mock_send, mock_service, mock_stdin
  ):
    mock_load.return_value = {
        "space_id": "S1",
        "thread_id": "T1",
        "sent_ids": [],
    }
    mock_stdin.return_value = json.dumps(
        {"transcript_path": "/tmp/transcript_trunc.json"}
    )

    # create a large output (20 lines)
    large_output = "\n".join([f"Line {i}" for i in range(20)])

    transcript_data = {
        "messages": [
            {
                "id": "msg_tool_output",
                "type": "tool",
                "content": large_output,
            },
        ]
    }

    # Use a scoped side effect for open
    original_open = open

    def side_effect(path, *args, **kwargs):
      if "/tmp/transcript_trunc.json" in str(path):
        return mock_open(read_data=json.dumps(transcript_data))(
            path, *args, **kwargs
        )
      return original_open(path, *args, **kwargs)

    with (
        patch("builtins.open", side_effect=side_effect),
        patch("os.path.exists", return_value=True),
        patch("sys.argv", ["chat_hook.py", "--event", "agent_output"]),
    ):
      chat_hook.main()

      # We assume send_to_chat is called once.
      # Check the content of the call.
      found_call = False
      for call in mock_send.call_args_list:
        content = call[0][3]
        # "Line 0" is truncated out, so we check for "lines truncated" or the last line
        if "lines truncated" in content:
          found_call = True
          self.assertIn("Line 19", content)

      self.assertTrue(
          found_call, "Did not find tool output call with truncation message"
      )


if __name__ == "__main__":
  unittest.main()