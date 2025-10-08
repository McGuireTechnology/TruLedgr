### Builder: export dependencies using Poetry
FROM python:3.11-slim AS builder

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR="/var/cache/pypoetry"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python - --version 1.7.1 && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Copy only pyproject/poetry.lock to leverage Docker cache
COPY pyproject.toml poetry.lock* /app/

# Export requirements.txt (without hashes) for pip install in the runtime image
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt

### Final image: small runtime with pip-installed deps
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements from builder and install
COPY --from=builder /app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

ENV PYTHONPATH=/app
ENV PORT=8080
EXPOSE 8080

# Use shell form so $PORT is expanded at runtime
CMD ["/bin/sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
