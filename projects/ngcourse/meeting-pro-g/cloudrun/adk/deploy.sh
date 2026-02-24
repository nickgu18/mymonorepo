#!/bin/bash
set -e

PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="meeting-pro-adk"
REGION="us-central1"

echo "Deploying $SERVICE_NAME to $PROJECT_ID in $REGION..."

gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --project $PROJECT_ID \
  --set-env-vars PROJECT_ID=$PROJECT_ID
