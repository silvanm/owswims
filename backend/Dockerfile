FROM python:3.8-slim

EXPOSE 8000
WORKDIR /code
CMD ["/bin/entrypoint.sh"]

COPY ./_docker/* /bin/

RUN apt update && apt install gettext -y && rm -rf /var/lib/apt/lists/*
RUN pip install poetry
RUN pip install gunicorn uvicorn uvloop httptools
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-dev
COPY . ./

RUN mkdir static

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
