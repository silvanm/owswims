#!/usr/bin/env bash
set -e
export $(egrep -v '^#' ./frontend/.env | xargs)

PROJECT_ID='owswims'

docker build --build-arg GOOGLE_MAPS_KEY \
	--build-arg GRAPHQL_ENDPOINT  -t gcr.io/${PROJECT_ID}/frontend:latest frontend/
docker build -t gcr.io/${PROJECT_ID}/backend:latest backend/

docker push gcr.io/${PROJECT_ID}/backend:latest
docker push gcr.io/${PROJECT_ID}/frontend:latest
