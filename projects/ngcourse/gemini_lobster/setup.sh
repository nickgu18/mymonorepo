#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIDGE_ROOT="$SCRIPT_DIR"
CONFIG_DIR="$HOME/.gemini_chat_bridge"

echo "🚀 Setting up Gemini Chat Bridge..."

# 1. Create config dir
mkdir -p "$CONFIG_DIR"

# 2. Virtual Environment
echo "📦 Setting up virtual environment..."
if [ ! -d "$CONFIG_DIR/venv" ]; then
    python3 -m venv "$CONFIG_DIR/venv"
fi
source "$CONFIG_DIR/venv/bin/activate"

# 3. Install Dependencies (Respecting User Preference for 'uv')
if command -v uv &> /dev/null; then
    echo "  - Using uv for package installation..."
    uv pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
else
    echo "  - 'uv' not found, using pip..."
    pip install --upgrade pip
    pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
fi

# 4. Shell Integration
SHELL_CONFIG=""
if [[ "$SHELL" == */zsh ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == */bash ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

if [ -n "$SHELL_CONFIG" ]; then
    echo "🐚 Configuring shell integration in $SHELL_CONFIG..."
    # Check if already added
    if grep -q "GEMINI_CHAT_BRIDGE_ROOT" "$SHELL_CONFIG"; then
        echo "  - Configuration might already exist, checking paths..."
        # We could try to update it, but for now just warn if it's different or let user handle.
        # Simple check:
        if grep -q "export GEMINI_CHAT_BRIDGE_ROOT=\"$BRIDGE_ROOT\"" "$SHELL_CONFIG"; then
             echo "  - Exact configuration already exists, skipping."
        else
             echo "  - Found existing GEMINI_CHAT_BRIDGE_ROOT but path might differ. Appending new config anyway (check for duplicates manually)."
             # Proceed to append
             echo "" >> "$SHELL_CONFIG"
             echo "# Gemini Chat Bridge Configuration (Updated)" >> "$SHELL_CONFIG"
             echo "export GEMINI_CHAT_BRIDGE_ROOT=\"$BRIDGE_ROOT\"" >> "$SHELL_CONFIG"
             echo "alias gemini_chat=\"\$HOME/.gemini_chat_bridge/venv/bin/python3 \$GEMINI_CHAT_BRIDGE_ROOT/chat_bridge_daemon.py -y\"" >> "$SHELL_CONFIG"
        fi
    else
        echo "" >> "$SHELL_CONFIG"
        echo "# Gemini Chat Bridge Configuration" >> "$SHELL_CONFIG"
        echo "export GEMINI_CHAT_BRIDGE_ROOT=\"$BRIDGE_ROOT\"" >> "$SHELL_CONFIG"
        echo "alias gemini_chat=\"\$HOME/.gemini_chat_bridge/venv/bin/python3 \$GEMINI_CHAT_BRIDGE_ROOT/chat_bridge_daemon.py -y\"" >> "$SHELL_CONFIG"
        echo "  - Added to $SHELL_CONFIG"
    fi
else
    echo "⚠️  Could not detect shell config file. Please manually add configuration."
fi

# 5. Link Extension
echo "🔗 Linking Gemini extension..."
if command -v gemini &> /dev/null; then
    gemini extension link "$BRIDGE_ROOT"
else
    echo "⚠️  'gemini' command not found. Skipping extension link."
    echo "    Please run 'gemini extension link \"$BRIDGE_ROOT\"' manually once gemini CLI is installed."
fi

# 6. Credentials
CREDENTIALS_FILE="$CONFIG_DIR/credentials.json"
if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "🔑 Google Cloud Credentials Setup"
    echo "You need to download your OAuth 2.0 Client ID JSON (Desktop Application) from Google Cloud Console."
    echo "Link: https://console.cloud.google.com/apis/credentials"
    echo "Please save it to: $CREDENTIALS_FILE"
    
    # Optional: Open URL if on a system that supports it (xdg-open is common on linux)
    if command -v xdg-open &> /dev/null; then
        read -p "Press Enter to open the Cloud Console in your browser..."
        xdg-open "https://console.cloud.google.com/apis/credentials"
    fi
    
    echo "Waiting for $CREDENTIALS_FILE to exist..."
    read -p "Press Enter once you have saved the file to continue verification..."
    
    if [ ! -f "$CREDENTIALS_FILE" ]; then
        echo "❌ File still not found at $CREDENTIALS_FILE"
        echo "   Please make sure to save it there."
    else
        echo "✅ Credentials found!"
    fi
else
    echo "✅ Credentials already exist."
fi

echo "🎉 Setup complete! Restart your shell or run 'source $SHELL_CONFIG' to start using 'gemini_chat'."
