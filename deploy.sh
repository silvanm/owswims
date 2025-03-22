#!/usr/bin/env bash
set -e
export $(egrep -v '^#' ./frontend/.env | xargs)

export GRAPHQL_ENDPOINT=/graphql
export GOOGLE_APPLICATION_CREDENTIALS=''

docker build --build-arg GOOGLE_MAPS_API_KEY --build-arg GRAPHQL_ENDPOINT \
    --build-arg GOOGLE_APPLICATION_CREDENTIALS \
    --build-arg DEFAULT_HEADER_PHOTO_URL \
	  -t gcr.io/owswims/app:latest .

docker push gcr.io/owswims/app:latest

gcloud config set project owswims
gcloud run deploy owswims --image gcr.io/owswims/app:latest --platform managed  --region=europe-west1
