#!/usr/bin/env bash
set -euo pipefail

# Launch helper for mlflow_llm_quickstart.py using Gemini 2.5 Flash.
# Usage: ./launch.sh demo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

run_demo() {
  echo "Installing dependencies (mlflow, google-generativeai)…"
  python -m pip install --upgrade "mlflow>=3.5" google-generativeai >/dev/null

  if [[ -f "$ENV_FILE" ]]; then
    echo "Loading env vars from ${ENV_FILE}"
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
  fi

  echo "Running mlflow_llm_quickstart.py"
  python "${SCRIPT_DIR}/mlflow_llm_quickstart.py"
}

TARGET=${1:-}

case "$TARGET" in
  demo)
    run_demo
    ;;
  "")
    echo "Usage: ./launch.sh demo" >&2
    exit 1
    ;;
  *)
    echo "Unknown target: ${TARGET}" >&2
    echo "Usage: ./launch.sh demo" >&2
    exit 1
    ;;
esac
