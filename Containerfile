# Use Python 3.13 Alpine as base image
FROM python:3.13-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apk add --no-cache \
    git \
    curl

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Create app directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./
COPY README.md ./

# Copy source code
COPY testing_farm_mcp/ ./testing_farm_mcp/

# Set fallback version for build
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_TESTING_FARM_MCP=0.1.0
ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.1.0

# Install dependencies using uv sync
RUN uv sync --frozen

# Set up the virtual environment in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Create non-root user
RUN adduser -D -s /bin/sh appuser && \
    chown -R appuser:appuser /app
USER appuser

# Default command
ENTRYPOINT ["testing-farm-mcp"]
