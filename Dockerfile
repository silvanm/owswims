#### STAGE 2 ####

FROM node:14 as frontend

COPY ./frontend/package.json ./frontend/yarn.lock ./

ENV PATH="./node_modules/.bin:$PATH"

ARG GOOGLE_MAPS_KEY

COPY frontend/ ./

RUN yarn install

RUN nuxt generate

#### STAGE 2 ####

FROM python:3.8-slim

EXPOSE 8000
WORKDIR /code
CMD ["/bin/entrypoint.sh"]

COPY backend/_docker/* /bin/

RUN apt update && apt install gettext -y && rm -rf /var/lib/apt/lists/*
RUN pip install poetry
RUN pip install gunicorn uvicorn uvloop httptools
COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-dev
COPY backend/ ./

ARG SECRET_KEY

COPY --from=frontend /dist/static/ /dist/index.html static/
RUN python ./manage.py collectstatic --noinput

ARG RELEASE_ID=''
ENV RELEASE_ID=$RELEASE_ID

ARG CI_COMMIT_REF_SLUG=''
ENV CI_COMMIT_REF_SLUG=$CI_COMMIT_REF_SLUG

ARG CI_COMMIT_SHA=''
ENV CI_COMMIT_SHA=$CI_COMMIT_SHA

ARG CI_BUILD_DATE=''
ENV CI_BUILD_DATE=$CI_BUILD_DATE

RUN echo "Commit Ref = ${CI_COMMIT_REF_SLUG} - Commit SHA = ${CI_COMMIT_SHA} - Built at = " ${CI_BUILD_DATE} > ./version
SHELL ["/bin/bash"]
