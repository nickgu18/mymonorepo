import unittest
import os
import sys

# Fix import path for google3 environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

from experimental.users.shayba.gemini_chat_bridge import chat_bridge_daemon

class TestArgsParsing(unittest.TestCase):

    def test_simple_args(self):

        space_id, cmd_args, space_name = chat_bridge_daemon.parse_args(["-v"])

        self.assertIsNone(space_id)

        self.assertIsNone(space_name)

        self.assertEqual(cmd_args, ["-v"])



    def test_space_name_flag(self):

        space_id, cmd_args, space_name = chat_bridge_daemon.parse_args(["--space-name", "My Space", "-v"])

        self.assertIsNone(space_id)

        self.assertEqual(space_name, "My Space")

        self.assertEqual(cmd_args, ["-v"])



    def test_space_name_equals(self):

        space_id, cmd_args, space_name = chat_bridge_daemon.parse_args(["--space-name=MySpace", "-v"])

        self.assertIsNone(space_id)

        self.assertEqual(space_name, "MySpace")

        self.assertEqual(cmd_args, ["-v"])



    def test_space_id_positional(self):

        space_id, cmd_args, space_name = chat_bridge_daemon.parse_args(["spaces/123", "-v"])

        self.assertEqual(space_id, "spaces/123")

        self.assertIsNone(space_name)

        self.assertEqual(cmd_args, ["-v"])



    def test_initial_prompt_i(self):

        space_id, cmd_args, space_name = chat_bridge_daemon.parse_args(["-i", "hello world"])

        self.assertIsNone(space_id)

        # Should be passed through

        self.assertEqual(cmd_args, ["-i", "hello world"])



    def test_initial_prompt_long(self):

        space_id, cmd_args, space_name = chat_bridge_daemon.parse_args(["--prompt-interactive", "hello"])

        self.assertEqual(cmd_args, ["--prompt-interactive", "hello"])



    def test_initial_prompt_equals(self):

        # NOTE: equals handling might need manual splitting if we want perfect pass-through,

        # but our loop currently just appends `arg` as is.

        # So `--prompt-interactive=hello` will be appended as a single arg. This is correct for pass-through.

        space_id, cmd_args, space_name = chat_bridge_daemon.parse_args(["--prompt-interactive=hello"])

        self.assertEqual(cmd_args, ["--prompt-interactive=hello"])



    def test_space_id_and_name_and_prompt(self):

        space_id, cmd_args, space_name = chat_bridge_daemon.parse_args(["spaces/123", "--space-name", "foo", "-i", "hello", "--other"])

        self.assertEqual(space_id, "spaces/123")

        self.assertEqual(space_name, "foo")

        self.assertEqual(cmd_args, ["-i", "hello", "--other"])



    def test_flag_looking_like_space_id_but_not_first(self):

        space_id, cmd_args, space_name = chat_bridge_daemon.parse_args(["-v", "spaces/query"])

        self.assertIsNone(space_id)

        self.assertEqual(cmd_args, ["-v", "spaces/query"])

if __name__ == "__main__":
    unittest.main()
