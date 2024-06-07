FROM debian:12-slim AS build
ARG POETRY_VERSION=1.8.3

RUN apt-get update && apt-get install -y --no-install-recommends --no-install-suggests \
    python3-venv libpython3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip setuptools && \
    /venv/bin/pip install poetry==${POETRY_VERSION}
