#!/bin/bash

# GitHub-specific deployment script for OWSwims
# This script can be used for manual deployments or local testing

set -e

echo "🚀 GitHub-based deployment script for OWSwims"

# Check if required environment variables are set
if [[ -z "$GCP_PROJECT_ID" ]]; then
    echo "What is the name of your GCP project?"
    read -r GCP_PROJECT_ID
    export GCP_PROJECT_ID
fi

if [[ -z "$GCP_REGION" ]]; then
    echo "What is your GCP region? (default: europe-west1)"
    read -r GCP_REGION
    GCP_REGION=${GCP_REGION:-europe-west1}
    export GCP_REGION
fi

# Set up gcloud configuration
echo "📋 Setting up gcloud configuration..."
gcloud config set project "$GCP_PROJECT_ID"

# Get the current git commit SHA
COMMIT_SHA=$(git rev-parse HEAD)
COMMIT_SHORT_SHA=$(git rev-parse --short HEAD)

echo "🏗️  Building the Docker image..."
echo "   Project: $GCP_PROJECT_ID"
echo "   Commit: $COMMIT_SHORT_SHA"

# Build and tag the image
CONTAINER_IMAGE="europe-docker.pkg.dev/$GCP_PROJECT_ID/owswims-repo/owswims"

docker build \
  --build-arg RELEASE_ID="$COMMIT_SHORT_SHA" \
  --build-arg CI_COMMIT_REF_SLUG="$(git branch --show-current)" \
  --build-arg CI_COMMIT_SHA="$COMMIT_SHA" \
  --build-arg CI_BUILD_DATE="$(date)" \
  --tag "$CONTAINER_IMAGE:latest" \
  --tag "$CONTAINER_IMAGE:$COMMIT_SHORT_SHA" \
  .

echo "📤 Pushing Docker image to Google Container Registry..."
gcloud builds submit . \
  --tag "$CONTAINER_IMAGE:latest" \
  --tag "$CONTAINER_IMAGE:$COMMIT_SHORT_SHA"

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy owswims \
  --image "$CONTAINER_IMAGE:$COMMIT_SHORT_SHA" \
  --platform managed \
  --region="$GCP_REGION" \
  --allow-unauthenticated

echo "✅ Deployment completed successfully!"
echo "🌐 Your application should be available at:"
gcloud run services describe owswims --region="$GCP_REGION" --format="value(status.url)"