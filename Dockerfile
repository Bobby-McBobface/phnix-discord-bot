FROM python:3.14-slim as builder

# Install Poetry
RUN pip3 install poetry==2.3.2
WORKDIR /app
COPY pyproject.toml poetry.lock /app/

# virtual env is created in "/app/.venv" directory  
ENV POETRY_NO_INTERACTION=1 \
POETRY_VIRTUALENVS_IN_PROJECT=1 \
POETRY_VIRTUALENVS_CREATE=true \
POETRY_CACHE_DIR=/tmp/poetry_cache

# Install dependencies
RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main --no-root
RUN poetry install

FROM python:3.14-slim as runner
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv
COPY src /app/src

ENTRYPOINT ["/app/.venv/bin/python", "src/bot.py"]
