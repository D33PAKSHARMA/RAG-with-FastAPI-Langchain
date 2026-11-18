FROM python:3.11-slim

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && rm -rf /var/lib/apt/lists/*

# Install uv tool
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /workspace

# Copy dependency configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies into system python via uv sync
RUN uv sync --frozen --no-dev

# Copy application code
COPY ./app ./app

EXPOSE 8000

# Run uvicorn server via uv environment
CMD ["/workspace/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]