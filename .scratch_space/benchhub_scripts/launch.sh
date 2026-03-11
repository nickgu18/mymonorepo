#!/bin/bash
set -e

# Point to the local Orchestrator backend
export ORCHESTRATOR_URL="http://localhost:8080"

# Load environment variables from .env if it exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# If no arguments are provided, run the default command
if [ $# -eq 0 ]; then
  uv --directory cli run cli.py submit --dataset swebench-verified@1.0 --model google/gemini-3-pro-preview
else
  # Otherwise, pass any provided arguments to the CLI
  uv --directory cli run cli.py submit "$@"
fi
