#!/usr/bin/env bash
set -e
export $(egrep -v '^#' ./frontend/.env | xargs)

PROJECT_ID='owswims'

export GRAPHQL_ENDPOINT=https://owswims-be-iyqeitbl7q-oa.a.run.app/graphql

docker build --build-arg GOOGLE_MAPS_KEY \
	--build-arg GRAPHQL_ENDPOINT  -t gcr.io/owswims/frontend:latest frontend/
docker build --build-arg SECRET_KEY=secret -t gcr.io/owswims/backend:latest backend/

docker push gcr.io/owswims/backend:latest
docker push gcr.io/owswims/frontend:latest

gcloud config set project owswims
gcloud run deploy owswims-fe --image gcr.io/owswims/frontend:latest --platform managed  --region=europe-west1
gcloud run deploy owswims-be --image gcr.io/owswims/backend:latest --platform managed --region=europe-west6
