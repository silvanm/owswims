#### STAGE 1 ####

FROM node:14   as frontend

WORKDIR /code

COPY ./frontend/package.json ./frontend/yarn.lock ./
RUN yarn install
RUN yarn build

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

RUN nuxt generate

#### STAGE 2 ####

FROM python:3.11-alpine

EXPOSE 8000
WORKDIR /code
CMD ["/bin/entrypoint.sh"]

COPY backend/_docker/* /bin/
RUN chmod +x /bin/entrypoint.sh

RUN apk add --no-cache bash gettext gcc musl-dev zlib-dev jpeg-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev
RUN pip install poetry
RUN pip install --only-binary=:all: gunicorn>=20.1.0 uvicorn>=0.14.0 uvloop httptools
COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root
COPY backend/ ./

ARG SECRET_KEY
ARG GOOGLE_APPLICATION_CREDENTIALS
ARG GOOGLE_MAPS_API_KEY
ARG FIRECRAWL_API_KEY
ARG SERPER_API_KEY
ARG OPENAI_API_KEY

COPY --from=frontend /code/dist/static/ /code/dist/index.html static/
RUN python ./manage.py collectstatic --noinput

RUN echo "Commit Ref = ${CI_COMMIT_REF_SLUG} - Commit SHA = ${CI_COMMIT_SHA} - Built at = " ${CI_BUILD_DATE} > ./version
