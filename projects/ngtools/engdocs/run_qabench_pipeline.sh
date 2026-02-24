#!/bin/bash

# A script to run the QABench automated pipeline.
# This script now uses a YAML configuration file to run the pipeline.

# Usage: ./run_qabench_pipeline.sh <path_to_config_file>

set -e # Exit immediately if a command exits with a non-zero status.

# Check if config file path is provided
if [ -z "$1" ]; then
  echo "Error: Please provide the path to the configuration file."
  echo "Usage: $0 <path_to_config_file>"
  exit 1
fi

CONFIG_FILE=$(realpath "$1")

echo "Running QABench pipeline with config: $CONFIG_FILE"
echo ""

# All poetry commands should be run from agent-prototypes directory.
if [ -d "agent-prototypes" ]; then
  cd agent-prototypes
else
  echo "Error: 'agent-prototypes' directory not found."
  echo "Please run this script from the root of the 'gcli' project."
  exit 1
fi


poetry run python agent_prototypes/scripts/qabench_pipeline.py \
  --config "$CONFIG_FILE"

echo ""
echo "Pipeline finished."
