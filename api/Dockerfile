FROM python:3.11-slim

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR="/var/cache/pypoetry"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python - --version 1.7.1 && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Copy only pyproject and poetry.lock first for caching
COPY pyproject.toml poetry.lock* /app/

# Install runtime dependencies
RUN poetry install --no-interaction --no-ansi --no-dev

# Copy application code
COPY . /app

ENV PYTHONPATH=/app

ENV PORT=8080
EXPOSE 8080

# Use shell form so environment variables like $PORT are expanded at container runtime
CMD ["/bin/sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
