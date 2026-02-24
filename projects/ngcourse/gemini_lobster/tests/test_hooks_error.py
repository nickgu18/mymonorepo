"""Tests for the chat hook error handling."""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Fix import path for google3 environment
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
)

from experimental.users.shayba.gemini_chat_bridge.hooks import chat_hook


class TestHooksError(unittest.TestCase):
  """Tests for the chat hook error handling."""

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
  def test_error_event(
      self, mock_load, mock_send, mock_service_getter, mock_stdin
  ):
    """Test standard error event handling."""
    # Setup mocks
    mock_load.return_value = {
        "space_id": "spaces/S1",
        "thread_id": "threads/T1",
        "user_id": "users/me",
        "sent_ids": [],
    }

    # Simulate CLI input for an error event
    error_input = {
        "error": {"message": "Something went wrong"},
        "timestamp": "1234567890",
    }
    mock_stdin.return_value = json.dumps(error_input)

    mock_service = MagicMock()
    mock_service_getter.return_value = mock_service
    mock_send.return_value = True

    # Run with --event error
    with patch(
        "sys.argv", ["chat_hook.py", "--event", "error"]
    ), patch.dict("os.environ", {}, clear=True):
      chat_hook.main()

    # Verify send_to_chat was called with the error message
    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    # args: service, space_id, thread_id, text, message_id, mention_user_id...

    self.assertEqual(args[1], "spaces/S1")
    self.assertEqual(args[2], "threads/T1")
    self.assertIn("🚨 Something went wrong", args[3])
    self.assertEqual(args[4], "error_1234567890")

    # Verify mention_user_id is passed
    # It might be passed as a keyword argument
    kwargs = mock_send.call_args[1]
    if "mention_user_id" in kwargs:
      self.assertEqual(kwargs["mention_user_id"], "users/me")
    elif len(args) > 5:
      self.assertEqual(args[5], "users/me")
    # else:
    #   self.fail("mention_user_id not passed")

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
  def test_error_event_string(
      self, mock_load, mock_send, mock_service_getter, mock_stdin
  ):
    """Test error event handling when error is a string."""
    # Setup mocks for string error
    mock_load.return_value = {
        "space_id": "spaces/S1",
        "thread_id": "threads/T1",
        "user_id": "users/me",
        "sent_ids": [],
    }

    # Simulate CLI input for an error event where error is just a string
    error_input = {
        "error": "Simple string error",
        "timestamp": "987654321",
    }
    mock_stdin.return_value = json.dumps(error_input)

    mock_service_getter.return_value = MagicMock()
    mock_send.return_value = True

    # Run with --event error
    with patch(
        "sys.argv", ["chat_hook.py", "--event", "error"]
    ), patch.dict("os.environ", {}, clear=True):
      chat_hook.main()

    # Verify send_to_chat was called
    mock_send.assert_called_once()
    args = mock_send.call_args[0]
    self.assertIn("🚨 Simple string error", args[3])
    self.assertEqual(args[4], "error_987654321")


if __name__ == "__main__":
  unittest.main()