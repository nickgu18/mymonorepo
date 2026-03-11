#!/bin/bash
set -e

# Configuration
PROJECT_ID="ai-incubation-team"
REGION="us-central1"
REPO_NAME="benchhub-repo"
ORCHESTRATOR_PORT=8080
ORCHESTRATOR_URL="http://localhost:$ORCHESTRATOR_PORT"

# 1. Build and Push Worker
TIMESTAMP=$(date +%s)
TAG="e2e-$TIMESTAMP"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/worker:$TAG"

echo "🛠️  Building and Pushing Worker Image: $TAG"
docker build -f worker/Dockerfile -t "$IMAGE" .
docker push "$IMAGE"

echo "✅ Worker image pushed: $IMAGE"

# 2. Start Orchestrator in Background
echo "🚀 Starting Orchestrator in background..."
export JOB_IMAGE="$IMAGE"
export PROJECT_ID="$PROJECT_ID"
export REGION="$REGION"

# Clean up on exit
trap 'kill $(jobs -p)' EXIT

# Ensure port is free
echo "🧹 Cleaning up port $ORCHESTRATOR_PORT..."
fuser -k "$ORCHESTRATOR_PORT"/tcp || true
sleep 1

# Start orchestrator
(cd orchestrator && uv run uvicorn main:app --port "$ORCHESTRATOR_PORT") > orchestrator.log 2>&1 &

# Wait for orchestrator to be ready
echo "Waiting for Orchestrator to be ready at $ORCHESTRATOR_URL..."
MAX_RETRIES=30
COUNT=0
while ! curl -s "$ORCHESTRATOR_URL/health" > /dev/null; do
    sleep 1
    COUNT=$((COUNT + 1))
    if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
        echo "❌ Orchestrator failed to start. Check orchestrator.log"
        exit 1
    fi
done
echo "✅ Orchestrator is ready!"

# 3. Run CLI
echo "🚀 Running CLI command..."
export ORCHESTRATOR_URL="$ORCHESTRATOR_URL"

if [ "$#" -gt 0 ]; then
    uv run --project cli python cli/cli.py "$@"
else
    # Default smoke test command
    echo "No arguments provided, running default check..."
    uv run --project cli python cli/cli.py submit --dataset swebench-verified@1.0 -t "django__django-11179"
fi
