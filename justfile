# Show the available recipes by default
default:
  just --list

# Start the MCP server
start:
    uv run testing-farm-mcp

# Install the package in development mode
install:
    uv sync --dev
    uv run pre-commit install

# Run static analysis
static-analysis:
    uv run pre-commit run --all-files

# Build the container image
image:
    podman build -t ghcr.io/thrix/testing-farm-mcp:latest .

# Build the container image
image-push:
    podman push ghcr.io/thrix/testing-farm-mcp:latest
