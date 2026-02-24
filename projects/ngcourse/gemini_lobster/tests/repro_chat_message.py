import json
import sys
import os
from unittest.mock import MagicMock, patch

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from hooks import chat_hook

def mock_send_to_chat(service, space_id, thread_id, text, message_id, mention_user_id=None):
    print(f"--- MSG ({message_id}) ---")
    print(text)
    print("-------------------------")
    return True

chat_hook.send_to_chat = mock_send_to_chat

# Mock data based on user report
tool_start_replace = {
    "tool_name": "replace",
    "tool_input": {
        "description": "Replaces text within a file. By default, replaces a single occurrence...",
        "expected_replacements": 1,
        "file_path": "/path/to/file.py",
        "new_string": "def new_func():\\n  pass",
        "old_string": "def old_func():\\n  pass",
        "instruction": "Rename the function"
    },
    "timestamp": "1"
}

tool_start_shell = {
    "tool_name": "run_shell_command",
    "tool_input": {
        "command": "ls -la",
        "description": "Lists files"
    },
    "timestamp": "2"
}

tool_output_generic = {
    "tool_name": "run_shell_command",
    "tool_response": {
        "stdout": "file1.txt\\nfile2.txt"
    },
    "timestamp": "2"
}

print("=== Simulating Tool Start (Replace) ===")
with patch("sys.stdin.read", return_value=json.dumps(tool_start_replace)), \
     patch("hooks.chat_hook.utils.get_authenticated_service"), \
     patch("hooks.chat_hook.utils.load_runtime_data", return_value={"space_id": "S", "thread_id": "T"}):
    sys.argv = ["chat_hook.py", "--event", "tool_start"]
    chat_hook.main()

print("\n=== Simulating Tool Start (Shell) ===")
with patch("sys.stdin.read", return_value=json.dumps(tool_start_shell)), \
     patch("hooks.chat_hook.utils.get_authenticated_service"), \
     patch("hooks.chat_hook.utils.load_runtime_data", return_value={"space_id": "S", "thread_id": "T"}):
    sys.argv = ["chat_hook.py", "--event", "tool_start"]
    chat_hook.main()

print("\n=== Simulating Tool Output (Shell) ===")
with patch("sys.stdin.read", return_value=json.dumps(tool_output_generic)), \
     patch("hooks.chat_hook.utils.get_authenticated_service"), \
     patch("hooks.chat_hook.utils.load_runtime_data", return_value={"space_id": "S", "thread_id": "T"}):
    sys.argv = ["chat_hook.py", "--event", "tool_output"]
    chat_hook.main()