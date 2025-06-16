# Testing Farm MCP Server

An MCP (Model Context Protocol) server for interacting with the Testing Farm service. This server provides tools to submit FMF-based test requests and list available composes for testing.

[![Container Build](https://github.com/thrix/testing-farm-mcp/actions/workflows/container-build.yml/badge.svg)](https://github.com/thrix/testing-farm-mcp/actions/workflows/container-build.yml)
[![Static Analysis](https://github.com/thrix/testing-farm-mcp/actions/workflows/static-analysis.yml/badge.svg)](https://github.com/thrix/testing-farm-mcp/actions/workflows/static-analysis.yml)

## Features

- **Submit Test Requests**: Submit test requests to Testing Farm
- **List Composes**: Retrieve available OS composes for testing from public or redhat ranches
- **Full Type Safety**: Built with static typing
- **Async Support**: Fully asynchronous API client using httpx
- **Container Ready**: Container images available

## Installation

### Option 1: Container (Recommended)

```bash
# Pull the latest container image
podman pull ghcr.io/thrix/testing-farm-mcp:latest

# Run the MCP server
podman run -i --rm -e TESTING_FARM_API_TOKEN="your-api-token-here"  ghcr.io/thrix/testing-farm-mcp:latest
```

### Option 2: Local Development

This project uses [uv](https://github.com/astral-sh/uv) for package management.

```bash
# Clone the repository
git clone https://github.com/thrix/testing-farm-mcp.git
cd testing-farm-mcp

# Install dependencies
just install
```

### Option 3: Using ToolHive

```bash
# Using ToolHive from Stacklok
systemctl start --user podman.socket
thv secret set TESTING_FARM_API_TOKEN
thv run ghcr.io/thrix/testing-farm-mcp:latest
```

## Configuration

Set the Testing Farm API token as an environment variable:

```bash
export TESTING_FARM_API_TOKEN="your-api-token-here"
```

## Usage

### Running the MCP Server

```bash
just start
```

### Available Tools

#### submit_request

Submit a FMF test request to Testing Farm.

**Parameters:**
- `url` (required): Git repository URL containing FMF metadata
- `ref` (optional): Branch, tag, or commit to test
- `merge_sha` (optional): Target commit SHA for merge testing
- `path` (optional): Path to metadata tree root
- `plan_name` (optional): Specific test plan to execute
- `plan_filter` (optional): Filter for tmt plans
- `test_name` (optional): Specific test to execute
- `test_filter` (optional): Filter for tmt tests
- `environments` (optional): Test environment configurations
- `notification` (optional): Notification settings
- `settings` (optional): Additional request settings
- `user` (optional): User information

**Example:**
```json
{
  "url": "https://github.com/example/test-repo",
  "ref": "main",
  "path": "/tests",
  "environments": [
    {
      "arch": "x86_64",
      "os": "fedora-38",
      "variables": {
        "TEST_VAR": "test_value"
      }
    }
  ]
}
```

#### list_composes

List available composes for a ranch.

**Parameters:**
- `ranch` (required): Ranch to query ("redhat" or "public")

**Example:**
```json
{
  "ranch": "public"
}
```

#### get_request

Get details about a Testing Farm request.

**Parameters:**
- `request_id` (required): Testing Farm request ID or a string containing the ID, like an API request URL or artifacts URL

**Example:**
```json
{
  "request_id": "12345678-1234-5678-9abc-123456789abc"
}
```

## Container Images

Container images are available on GitHub Container Registry:

- `ghcr.io/thrix/testing-farm-mcp:latest` - Latest stable version

Supported architectures:
- `linux/amd64`

## Development

### Setup Development Environment

```bash
# Install development dependencies
just install
```

### Code Quality

This project uses several tools for code quality:

- **ruff**: Linting and formatting
- **codespell**: Spell checking
- **mypy**: Type checking (excluding tests)
- **pre-commit**: Git hook management

```bash
just static-analysis
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

Make sure to follow the existing code style and add tests for new functionality.

## License

Apache-2.0 License - see LICENSE file for details.
