# Gemini Chat Bridge

This project links the Gemini CLI with Google Chat, allowing you to interact with your local Gemini instance directly from a Google Chat space.

## 🚀 Key Features

-   **Stateless "One-Shot" Interaction**: Each message from Chat triggers a fresh, isolated invocation of the Gemini CLI. This ensures robust, predictable behavior without hanging processes or complex PTY state.
-   **Persistent Sessions**: Conversation history is automatically managed and stored in JSON files (`~/.gemini_chat_bridge/sessions/`). Context is preserved across daemon restarts.
-   **Smart Summarization**: Long conversations are automatically summarized to maintain a strict context window while preserving key information.
-   **Multi-User & Multi-Thread**: Tracks individual users and threads, maintaining separate conversation histories for each context.
-   **Strict Mention Mode**: The bridge only responds when explicitly mentioned (e.g., `@Lobster` or `@Gemini`) or when using the `@lobster` trigger word, preventing accidental interruptions.
-   **Alias Support**: Automatically respects your local shell's `gemini` alias and configuration.

## 🛠 Installation & Setup

### 1. Google Cloud Credentials

The bridge requires a Google Cloud project with the **Google Chat API** enabled to interact with Chat.

1.  **Create a Project**: Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2.  **Enable Chat API**: Search for "Google Chat API" in the library and enable it.
3.  **Create OAuth Credentials**:
    *   Go to **APIs & Services** > **Credentials**.
    *   Click **Create Credentials** > **OAuth client ID**.
    *   Select **Desktop application** as the application type.
    *   Name it `Gemini Chat Bridge`.
    *   Click **Create** and download the JSON file.
4.  **Save Credentials**:
    *   Rename the downloaded file to `credentials.json`.
    *   Place it in the bridge configuration directory:
        ```bash
        mkdir -p ~/.gemini_chat_bridge
        mv /path/to/downloaded-credentials.json ~/.gemini_chat_bridge/credentials.json
        ```

### 2. Run Setup Script

The included setup script automates the rest of the installation:

```bash
./setup.sh
```

This will:
*   Create a Python virtual environment.
*   Install required dependencies (`google-api-python-client`, etc.).
*   Link the extension to the Gemini CLI.

### 3. Shell Integration

Add the following to your `~/.zshrc` or `~/.bashrc` to easily control the bridge:

```bash
# Gemini Chat Bridge Configuration
# Point this to the location of the bridge code
export GEMINI_CHAT_BRIDGE_ROOT="/path/to/gemini_chat_bridge"

# Alias to run the daemon
alias gemini_chat="$HOME/.gemini_chat_bridge/venv/bin/python3 $GEMINI_CHAT_BRIDGE_ROOT/chat_bridge_daemon.py"
```

*(Note: If you used `./setup.sh`, it may have already suggested these lines).*

## ⚙️ Development & Overrides

If you are modifying the bridge code locally:

```bash
source manage_override.sh set    # Use local code and hooks
source manage_override.sh reset  # Revert to submitted google3 head
source manage_override.sh status # Check current mode
```

## 💬 How to Use

1.  **Start the Daemon**:
    ```bash
    gemini_chat
    ```
2.  **Authenticate**: On first run, a browser window (or terminal link) will appear to authenticate with your Google account.
3.  **Interact**:
    *   Go to Google Chat and ensure the account you authenticated with has access.
    *   Send a message mentioning the bot/trigger:
        > @Lobster List the files in the current directory.
    *   The bridge will run the command locally and reply with the output.

### Session Management

*   **Storage**: Sessions are saved in `~/.gemini_chat_bridge/sessions/`.
*   **Isolation**: Each user has a unique session file (e.g., `user_12345.json`).
*   **Summarization**: When a conversation exceeds 20 turns, the bridge automatically summarizes the history to save context space.

### Chat Commands

*   `/yolo`: Toggle "YOLO mode" (auto-approval of tools) for the session.
*   `/exit`: Gracefully shut down the daemon.
