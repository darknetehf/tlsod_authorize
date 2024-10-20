FROM python:3.13-alpine AS base

ARG DEV=false
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN apk update && \
    apk add libpq


FROM base AS builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apk update && \
    apk add musl-dev build-base gcc gfortran openblas-dev

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.4

# Install the app
COPY pyproject.toml poetry.lock README.rst ./
COPY src/ ./src

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

FROM base AS runtime

COPY --from=builder /app /app

# switch to non-privileged user
RUN addgroup -S tlsod && adduser -S tlsod -G tlsod
USER tlsod

CMD ["tlsod-authorize", "--db=/data/domains.sqlite", "--port=8080"]
