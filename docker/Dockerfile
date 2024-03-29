FROM python:3.11-alpine as base

ARG DEV=false
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN apk update && \
    apk add libpq


FROM base as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apk update && \
    apk add musl-dev build-base gcc gfortran openblas-dev

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.7.1

# Install the app
COPY pyproject.toml poetry.lock README.rst ./
COPY src/ ./src

# RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR
RUN poetry install --without dev

FROM base as runtime

COPY --from=builder /app /app

CMD ["tlsod-authorize", "--db=/data/domains.sqlite", "--port=8080"]
