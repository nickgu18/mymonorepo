#!/bin/bash

set -e

# The project root is three levels up from the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SKILL_BASE_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$SKILL_BASE_DIR")"

TEMPLATE_FILE="$SCRIPT_DIR/template.md"
if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "Error: template file not found at $TEMPLATE_FILE"
  exit 1
fi

if [ -n "$1" ]; then
  OUTPUT_DIR="$1"
else
  OUTPUT_DIR="$SKILL_BASE_DIR"
fi

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Generate a timestamp for the filename
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
NEW_TASK_FILE="$OUTPUT_DIR/$TIMESTAMP.md"

echo "Creating new task file: $NEW_TASK_FILE"
cp "$TEMPLATE_FILE" "$NEW_TASK_FILE"
echo "Task file created successfully."
