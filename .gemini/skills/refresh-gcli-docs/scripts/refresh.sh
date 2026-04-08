#!/bin/bash
set -e

# Resolve monorepo root (4 levels up from .gemini/skills/refresh-gcli-docs/scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"
TEMP_DIR="/tmp/gemini_cli_docs_refresh"
REPO_URL="https://github.com/google-gemini/gemini-cli.git"
TARGET_DIR="$MONOREPO_ROOT/docs/gcli"

echo "Monorepo root: $MONOREPO_ROOT"
echo "Refreshing Gemini CLI docs..."

rm -rf "$TEMP_DIR"
git clone --depth 1 "$REPO_URL" "$TEMP_DIR"

mkdir -p "$TARGET_DIR"
cp -r "$TEMP_DIR/docs/"* "$TARGET_DIR/"

rm -rf "$TEMP_DIR"

echo "Gemini CLI docs refreshed successfully."
