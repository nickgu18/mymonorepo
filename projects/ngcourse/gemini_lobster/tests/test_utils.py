import unittest
import os
import sys

# Fix import path for google3 environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

from experimental.users.shayba.gemini_chat_bridge import utils

class TestUtils(unittest.TestCase):

  def test_clean_text_ansi(self):
    text = "\x1b[31mHello\x1b[0m \x1b[1mWorld\x1b[0m"
    self.assertEqual(utils.clean_text(text), "Hello World")

  def test_clean_text_ui(self):
    box = "╭─╮\n│A│\n╰─╯"
    self.assertEqual(utils.clean_text(box), "A")

    spinner = "⠋ Processing..."
    self.assertEqual(utils.clean_text(spinner), "Processing...")

  def test_clean_text_cli_ui(self):
    """Tests filtering of Gemini CLI UI elements."""
    garbage = (
        "Prioritizing a Direct Response (esc to cancel, 3s)\n1 context file    "
        "                                                                      "
        "         YOLO mode (ctrl + y to toggle)\n*   Type your message or"
        " @path/to/file\n~                                                    "
        " no sandbox (see /docs)                                               "
        "      gemini-3-flash-preview /model\nClarifying Initial Response (esc"
        " to cancel, 4s)\n✦ Hello! How can I help you?"
    )
    cleaned = utils.clean_text(garbage)
    self.assertNotIn("Prioritizing", cleaned)
    self.assertNotIn("YOLO mode", cleaned)
    self.assertNotIn("Type your message", cleaned)
    self.assertNotIn("no sandbox", cleaned)
    self.assertIn("Hello! How can I help you?", cleaned)

  def test_clean_text_nag(self):
    nag = (
        "You are currently in screen reader-friendly view. This will be"
        " remembered for the next run.\nActual Content"
    )
    self.assertEqual(utils.clean_text(nag), "Actual Content")

  def test_strip_reasoning(self):
    # ✦ prefix
    self.assertEqual(
        utils.strip_reasoning("✦ The answer is 42"), "The answer is 42"
    )

    # Block structure with long reasoning
    text = "Reasoning: " + "A" * 100 + "\n\nActual Answer"
    self.assertEqual(utils.strip_reasoning(text), "Actual Answer")

    # Multi-block reasoning
    text = "Part 1\n\nPart 2\n\nFinal Answer"
    self.assertEqual(utils.strip_reasoning(text), "Final Answer")

  def test_get_content_id(self):
    content = "Hello World"
    content_id = utils.get_content_id(content)
    self.assertEqual(len(content_id), 12)
    self.assertEqual(content_id, utils.get_content_id(content))
    self.assertNotEqual(content_id, utils.get_content_id("Different"))


if __name__ == "__main__":
    unittest.main()
