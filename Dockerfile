#### STAGE 1 ####

FROM node:20 AS frontend

WORKDIR /code

COPY ./frontend/package.json ./frontend/package-lock.json ./
RUN npm ci

ENV PATH="./node_modules/.bin:$PATH"

ARG GOOGLE_MAPS_API_KEY
ARG RAPIDAPI_KEY
ARG GRAPHQL_ENDPOINT
ARG DEFAULT_HEADER_PHOTO_URL
ARG RELEASE_ID=''
ENV RELEASE_ID=$RELEASE_ID
ARG CI_COMMIT_REF_SLUG=''
ENV CI_COMMIT_REF_SLUG=$CI_COMMIT_REF_SLUG
ARG CI_COMMIT_SHA=''
ENV CI_COMMIT_SHA=$CI_COMMIT_SHA
ARG CI_BUILD_DATE=''
ENV CI_BUILD_DATE=$CI_BUILD_DATE

COPY frontend/ ./

RUN npx nuxt build

#### STAGE 2 ####

FROM python:3.11-slim

EXPOSE 8000
WORKDIR /code
CMD ["/bin/entrypoint.sh"]

COPY backend/_docker/* /bin/
RUN chmod +x /bin/entrypoint.sh

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash gettext gcc libc6-dev zlib1g-dev libjpeg-dev \
    libfreetype-dev liblcms2-dev libopenjp2-7-dev libtiff-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install uv
RUN pip install --only-binary=:all: gunicorn>=20.1.0 uvicorn>=0.22.0
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
ENV PATH="/code/.venv/bin:$PATH"
COPY backend/ ./

ARG SECRET_KEY
ARG GOOGLE_APPLICATION_CREDENTIALS
ARG GOOGLE_MAPS_API_KEY

COPY --from=frontend /code/.output/public/ static/
# Nuxt i18n's prefix strategy makes /index.html a redirect to /en.
# Copy the real SPA shell over so Django serves the app, not a redirect.
RUN cp static/en/index.html static/index.html
RUN python ./manage.py collectstatic --noinput

RUN echo "Commit Ref = ${CI_COMMIT_REF_SLUG} - Commit SHA = ${CI_COMMIT_SHA} - Built at = " ${CI_BUILD_DATE} > ./version
