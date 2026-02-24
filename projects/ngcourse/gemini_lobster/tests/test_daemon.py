import json
import os
import socket
import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

# Fix import path for google3 environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

from experimental.users.shayba.gemini_chat_bridge import chat_bridge_daemon
from experimental.users.shayba.gemini_chat_bridge import utils

class TestDaemon(unittest.TestCase):

  @patch(
      "experimental.users.shayba.gemini_chat_bridge.utils.get_authenticated_service"
  )
  @patch(
      "experimental.users.shayba.gemini_chat_bridge.chat_bridge_daemon.ChatDaemon.ensure_space"
  )
  def test_daemon_init(self, mock_ensure_space, mock_get_service):
    mock_ensure_space.return_value = "spaces/123"
    daemon = chat_bridge_daemon.ChatDaemon(None, ["--some-arg"])
    self.assertEqual(daemon.space_id, "spaces/123")
    self.assertEqual(daemon.cmd_args, ["--some-arg"])

  @patch("os.path.exists")
  @patch("os.getcwd")
  @patch("builtins.open", new_callable=mock_open, read_data="{}")
  def test_ensure_space_new(self, mock_file, mock_getcwd, mock_exists):
    mock_getcwd.return_value = "/path/to/my_project"
    mock_exists.return_value = False

    mock_service = MagicMock()
    mock_service.spaces().setup().execute.return_value = {
        "name": "spaces/new_id"
    }
    # Mock list to return empty spaces so creation proceeds
    mock_service.spaces().list().execute.return_value = {}

    with patch(
        "experimental.users.shayba.gemini_chat_bridge.utils.get_authenticated_service",
        return_value=mock_service,
    ):
      daemon = chat_bridge_daemon.ChatDaemon("spaces/already_set", [])
      # This doesn't call ensure_space because space_id is provided
      self.assertEqual(daemon.space_id, "spaces/already_set")

      # Now test ensure_space directly
      daemon.space_id = None
      space_id = daemon.ensure_space()
      self.assertEqual(space_id, "spaces/new_id")

      # Verify robot emoji in call
      args, kwargs = mock_service.spaces().setup.call_args
      display_name = kwargs["body"]["space"]["display_name"]
      self.assertIn("🤖 Gemini:", display_name)
      self.assertIn("my_project", display_name)

      # Verify notification setting update
      mock_service.users().spaces().spaceNotificationSetting().patch.assert_called_once()
      n_args, n_kwargs = (
          mock_service.users()
          .spaces()
          .spaceNotificationSetting()
          .patch.call_args
      )
      self.assertEqual(
          n_kwargs["name"], "users/me/spaces/new_id/spaceNotificationSetting"
      )
      self.assertEqual(n_kwargs["body"]["notification_setting"], "FOR_YOU")

  @patch("os.path.exists")
  @patch("os.getcwd")
  @patch("builtins.open", new_callable=mock_open, read_data="{}")
  def test_ensure_space_reuse(self, mock_file, mock_getcwd, mock_exists):
    mock_getcwd.return_value = "/path/to/my_project"
    mock_exists.return_value = False

    mock_service = MagicMock()
    # Mock matching existing space
    mock_service.spaces().list().execute.return_value = {
        "spaces": [{"name": "spaces/existing_id", "displayName": "🤖 MySpace"}]
    }

    with patch(
        "experimental.users.shayba.gemini_chat_bridge.utils.get_authenticated_service",
        return_value=mock_service,
    ):
      # Pass space_name to match
      daemon = chat_bridge_daemon.ChatDaemon(
          "spaces/temp", [], space_name="MySpace"
      )

      # Force run ensure_space
      daemon.space_id = None
      space_id = daemon.ensure_space()

      self.assertEqual(space_id, "spaces/existing_id")

      # Verify list called
      mock_service.spaces().list.assert_called()
      # Verify setup NOT called
      mock_service.spaces().setup.assert_not_called()

      # Verify notification setting IS updated even for reused spaces
      mock_service.users().spaces().spaceNotificationSetting().patch.assert_called_once()
      n_args, n_kwargs = (
          mock_service.users()
          .spaces()
          .spaceNotificationSetting()
          .patch.call_args
      )
      self.assertEqual(
          n_kwargs["name"],
          "users/me/spaces/existing_id/spaceNotificationSetting",
      )
      self.assertEqual(n_kwargs["body"]["notification_setting"], "FOR_YOU")

  @patch("subprocess.run")
  @patch(
      "experimental.users.shayba.gemini_chat_bridge.utils.get_authenticated_service"
  )
  def test_rename_space_with_gemini(self, mock_get_service, mock_run):
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service

    # Mock gemini output
    mock_run.return_value = MagicMock(
        stdout="Refactoring Project\n", returncode=0
    )

    daemon = chat_bridge_daemon.ChatDaemon("spaces/123", [])
    daemon.rename_space_with_gemini()

    # Verify patch call
    mock_service.spaces().patch.assert_called_once()
    patch_body = mock_service.spaces().patch.call_args[1]["body"]
    self.assertEqual(patch_body["displayName"], "🤖 Refactoring Project")

    # Verify notification message
    mock_service.spaces().messages().create.assert_called_once()
    msg_body = mock_service.spaces().messages().create.call_args[1]["body"]
    self.assertIn("Refactoring Project", msg_body["text"])

  @patch(
      "experimental.users.shayba.gemini_chat_bridge.utils.get_authenticated_service"
  )
  def test_input_poller_triggers_typing(self, mock_get_service):
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service

    daemon = chat_bridge_daemon.ChatDaemon("spaces/123", [])
    daemon.last_message_time = "2023-01-01T00:00:00Z"

    # Mock a human message
    mock_service.spaces().messages().list().execute.return_value = {
        "messages": [{
            "createTime": "2023-01-01T00:00:01Z",
            "text": "Hello Gemini",
            "sender": {"type": "HUMAN"},
        }]
    }

    # We need to run input_poller logic once.
    # Since it's a loop, we can mock time.sleep to raise an exception after one iteration.
    with (
        patch("time.sleep", side_effect=[None, InterruptedError]),
        patch("os.write"),
        patch(
            "experimental.users.shayba.gemini_chat_bridge.utils.load_runtime_data",
            return_value={},
        ),
        patch(
            "experimental.users.shayba.gemini_chat_bridge.utils.save_runtime_data"
        ),
    ):
      try:
        daemon.input_poller()
      except InterruptedError:
        pass

    self.assertTrue(daemon.typing_event.is_set())

  @patch("os.getcwd")
  @patch(
      "experimental.users.shayba.gemini_chat_bridge.utils.get_authenticated_service"
  )
  def test_ensure_space_cwd_error(self, mock_get_service, mock_getcwd):
    # Simulate OSError when calling os.getcwd()
    mock_getcwd.side_effect = OSError("Transport endpoint is not connected")

    mock_service = MagicMock()
    mock_get_service.return_value = mock_service

    # Mock list to return empty so it tries to create a new space
    mock_service.spaces().list().execute.return_value = {}
    # Mock setup to return a new space ID
    mock_service.spaces().setup().execute.return_value = {
        "name": "spaces/new_fallback_id"
    }

    daemon = chat_bridge_daemon.ChatDaemon(None, [])

    # Ensure it didn't crash and returned the new ID
    self.assertEqual(daemon.space_id, "spaces/new_fallback_id")

    # Verify the name used for the space contains "unknown"
    args, kwargs = mock_service.spaces().setup.call_args
    display_name = kwargs["body"]["space"]["display_name"]
    self.assertIn("🤖 Gemini: unknown", display_name)

  @patch(
      "experimental.users.shayba.gemini_chat_bridge.chat_bridge_daemon.logger"
  )
  @patch(
      "experimental.users.shayba.gemini_chat_bridge.utils.get_authenticated_service"
  )
  def test_input_poller_network_error(self, mock_get_service, mock_logger):
    mock_service = MagicMock()
    mock_get_service.return_value = mock_service

    daemon = chat_bridge_daemon.ChatDaemon("spaces/123", [])

    # Raise socket.error (to ensure we are catching the right thing)
    mock_service.spaces().messages().list().execute.side_effect = socket.error(
        "Socket fail"
    )

    # Run poller once.
    # First sleep (start of loop) -> None
    # execute -> raises socket.error -> caught -> logs debug -> calls sleep (backoff)
    # Second sleep (backoff) -> raise RuntimeError to stop test
    with patch("time.sleep", side_effect=[None, RuntimeError("Stop loop")]):
      try:
        daemon.input_poller()
      except RuntimeError:
        pass

    # Verify execute was called
    mock_service.spaces().messages().list().execute.assert_called()

    # Verify debug log was called
    mock_logger.debug.assert_called()
    args, _ = mock_logger.debug.call_args
    self.assertIn("Transient network error", args[0])
    self.assertIn("Socket fail", str(args[1]))

    # Verify exception was NOT logged
    mock_logger.exception.assert_not_called()


if __name__ == "__main__":
    unittest.main()
