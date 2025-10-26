#!/bin/bash

# GitHub-specific deployment script for OWSwims
# This script can be used for manual deployments or local testing

set -e

echo "🚀 GitHub-based deployment script for OWSwims"

# Check if required environment variables are set
export GCP_PROJECT_ID=${GCP_PROJECT_ID:-mpom-shared}
export GCP_REGION=${GCP_REGION:-europe-west6}
export KUBE_NAMESPACE=owswims
    
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
  --platform linux/amd64 \
  --build-arg RELEASE_ID="$COMMIT_SHORT_SHA" \
  --build-arg CI_COMMIT_REF_SLUG="$(git branch --show-current)" \
  --build-arg CI_COMMIT_SHA="$COMMIT_SHA" \
  --build-arg CI_BUILD_DATE="$(date)" \
  --build-arg GOOGLE_MAPS_API_KEY="${GOOGLE_MAPS_API_KEY:-}" \
  --build-arg RAPIDAPI_KEY="${RAPIDAPI_KEY:-}" \
  --build-arg GRAPHQL_ENDPOINT="${GRAPHQL_ENDPOINT:-}" \
  --build-arg DEFAULT_HEADER_PHOTO_URL="${DEFAULT_HEADER_PHOTO_URL:-https://storage.googleapis.com/owswims-prod/photos/default-image.jpg}" \
  --build-arg SECRET_KEY="${SECRET_KEY:-dfgim4p02mi2mg2eign2}" \
  --build-arg SENTRY_DSN="${SENTRY_DSN:-}" \
  --tag "$CONTAINER_IMAGE:latest" \
  --tag "$CONTAINER_IMAGE:$COMMIT_SHORT_SHA" \
  .

echo "📤 Pushing Docker image to Google Container Registry..."
docker push "$CONTAINER_IMAGE:latest"
docker push "$CONTAINER_IMAGE:$COMMIT_SHORT_SHA"

K8S_CLUSTER=${K8S_CLUSTER:-mpom-shared-k8s}
echo "📦 Getting GKE credentials..."
# Prompt for K8S cluster name and namespace if not set
if [[ -z "$K8S_CLUSTER" ]]; then
    echo "What is the name of your GKE cluster?"
    read -r K8S_CLUSTER
    export K8S_CLUSTER
fi

# Install GKE auth plugin if not already installed
echo "🔧 Setting up GKE authentication..."
export USE_GKE_GCLOUD_AUTH_PLUGIN=True

# Get GKE credentials
gcloud container clusters get-credentials "$K8S_CLUSTER" \
  --region "$GCP_REGION" \
  --project "$GCP_PROJECT_ID"

export KUBE_NAMESPACE=${KUBE_NAMESPACE:-owswims}
echo "🚀 Deploying to Kubernetes with Helm..."
helm upgrade --install owswims -f helm/values.yaml helm/ \
  --namespace "$KUBE_NAMESPACE" \
  --create-namespace \
  --set-string image.tag="$COMMIT_SHORT_SHA"

echo "✅ Deployment completed successfully!"
echo "📊 Deployment details:"
echo "   - Namespace: $KUBE_NAMESPACE"
echo "   - Image tag: $COMMIT_SHORT_SHA"