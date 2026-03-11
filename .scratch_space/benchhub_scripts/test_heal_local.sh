#!/bin/bash
set -e

# ==============================================================================
# Local Heal Run Tester
# Simulates the Orchestrator triggering a heal job on the local Docker worker.
# ==============================================================================

# Target run to heal
TARGET_RUN_ID="benchhub-eval-5f1d7fea"
# Generate a mock batch job id to simulate a new Cloud Batch attempt
MOCK_BATCH_ID="${TARGET_RUN_ID}-heal-local-$(date +%s)"

# Ensure you have your credentials ready
# Because you are using `sudo` to run docker, $HOME resolves to /root, but your gcloud 
# credentials are saved in /usr/local/google/home/guyu/.config/gcloud.
# We'll explicitly point to your user directory.
USER_HOME="/usr/local/google/home/guyu"
CREDENTIALS_FILE="$USER_HOME/.config/gcloud/application_default_credentials.json"

if [ ! -f "$CREDENTIALS_FILE" ]; then
  echo "❌ Error: Google Cloud credentials not found at $CREDENTIALS_FILE"
  echo "Please run: gcloud auth application-default login (without sudo)"
  exit 1
fi

# Load GITHUB_TOKEN directly from .env file so we don't need to pass it
if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" = "dummy" ]; then
  echo "❌ Error: GITHUB_TOKEN environment variable could not be loaded from .env."
  exit 1
fi

echo "🚀 Building local worker image..."
docker build -f worker/Dockerfile -t worker:local-test .

echo "🔥 Starting simulated heal run for $TARGET_RUN_ID..."
echo "Using MOCK_BATCH_ID: $MOCK_BATCH_ID"

docker run --rm \
  -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json \
  -e PROJECT_ID="ai-incubation-team" \
  -e REGION="us-central1" \
  -e GCS_BUCKET="my-harbor-results-bucket" \
  -e ARTIFACTS_BUCKET="benchhub-artifacts" \
  -e JOBS_TABLE="ai-incubation-team.evals.eval_results_jobs" \
  -e INSTANCES_TABLE="ai-incubation-team.evals.eval_results_instances" \
  -e BENCHHUB_RUN_ID="$TARGET_RUN_ID" \
  -e RESUME_FROM_RUN_ID="$TARGET_RUN_ID" \
  -e BATCH_JOB_ID="$MOCK_BATCH_ID" \
  -e GITHUB_TOKEN="${GITHUB_TOKEN}" \
  -v "$USER_HOME/.config/gcloud:/root/.config/gcloud:ro" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  worker:local-test

echo "✅ Local test complete. Check BigQuery to ensure $MOCK_BATCH_ID was inserted correctly!"
