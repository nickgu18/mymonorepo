#!/bin/bash

# Default submitted path in google3 head
SUBMITTED_ROOT="/google/src/head/depot/google3/experimental/users/shayba/gemini_chat_bridge"
GEMINI_BIN="/google/bin/releases/gemini-cli/tools/gemini"

# Detect if the script is being sourced or run
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: This script must be sourced to apply environment changes."
    echo "Usage: source manage_override.sh [set|reset|status]"
    exit 1
fi

# Determine the absolute path of this workspace
CURRENT_WORKSPACE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

case "$1" in
    set)
        export GEMINI_CHAT_BRIDGE_ROOT="$CURRENT_WORKSPACE_ROOT"
        export GEMINI_CLI_HOOKS_QUIET=true
        echo "✅ GEMINI_CHAT_BRIDGE_ROOT set to: $GEMINI_CHAT_BRIDGE_ROOT"
        
        echo "🔗 Linking Gemini extension to local workspace..."
        $GEMINI_BIN extension uninstall chat-bridge > /dev/null 2>&1
        yes | $GEMINI_BIN extension link "$GEMINI_CHAT_BRIDGE_ROOT" > /dev/null 2>&1
        echo "🚀 All set! gemini_chat (via alias) and hooks are now running from this workspace."
        ;;
    reset)
        export GEMINI_CHAT_BRIDGE_ROOT="$SUBMITTED_ROOT"
        export GEMINI_CLI_HOOKS_QUIET=true
        echo "🔄 GEMINI_CHAT_BRIDGE_ROOT reset to: $GEMINI_CHAT_BRIDGE_ROOT"
        
        echo "🔗 Linking Gemini extension back to submitted path..."
        $GEMINI_BIN extension uninstall chat-bridge > /dev/null 2>&1
        yes | $GEMINI_BIN extension link "$GEMINI_CHAT_BRIDGE_ROOT" > /dev/null 2>&1
        echo "🏠 Done. Using submitted code from google3 head."
        ;;
    status)
        echo "Current GEMINI_CHAT_BRIDGE_ROOT: $GEMINI_CHAT_BRIDGE_ROOT"
        if [[ "$GEMINI_CHAT_BRIDGE_ROOT" == "$CURRENT_WORKSPACE_ROOT" ]]; then
            echo "Status: 🛠️ OVERRIDDEN (Current Workspace)"
        elif [[ "$GEMINI_CHAT_BRIDGE_ROOT" == "$SUBMITTED_ROOT" ]]; then
            echo "Status: 🏠 SUBMITTED (Google3 Head)"
        else
            echo "Status: ❓ UNKNOWN PATH"
        fi
        ;;
    *)
        echo "Usage: source manage_override.sh [set|reset|status]"
        echo "  set:    Run code/hooks from THIS workspace ($CURRENT_WORKSPACE_ROOT)"
        echo "  reset:  Run code/hooks from submitted path ($SUBMITTED_ROOT)"
        echo "  status: Show current override status"
        ;;
esac
