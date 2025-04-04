FROM python:3.13-alpine AS base

ARG DEV=false
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN apk update

FROM base AS builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Install Poetry
RUN pip install poetry==2.1.1

# Install the app
COPY pyproject.toml poetry.lock README.rst ./
COPY src/ ./src

RUN poetry install && rm -rf $POETRY_CACHE_DIR

FROM base AS runtime

RUN addgroup -S tlsod && adduser -S tlsod -G tlsod

COPY --chown=tlsod:root --from=builder /app /app

# switch to non-privileged user
USER tlsod

ENTRYPOINT ["tlsod-authorize"]
CMD ["--db=/data/domains.sqlite", "--port=8080"]
