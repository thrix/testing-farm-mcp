"""Testing Farm MCP Server."""

import re
from enum import StrEnum
from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field

from testing_farm_mcp.client import TestingFarmClient


class Ranch(StrEnum):
    """Available ranch options for Testing Farm."""

    redhat = "redhat"
    public = "public"


class Architecture(StrEnum):
    """Supported architectures."""

    x86_64 = "x86_64"
    aarch64 = "aarch64"
    ppc64le = "ppc64le"
    s390x = "s390x"


mcp = FastMCP("Testing Farm MCP Server")


@mcp.tool()  # type: ignore[misc]
async def submit_request(  # noqa: PLR0913
    url: Annotated[
        str,
        Field(
            ...,
            description="Git repository URL containing the tmt metadata.",
        ),
    ],
    compose: Annotated[
        str,
        Field(
            ...,
            description="Compose to run tests against.",
        ),
    ],
    ref: Annotated[
        str,
        Field(
            description="Git branch, tag or commit specifying the desired git revision.",
        ),
    ] = "main",
    metadata_root_dir: Annotated[
        str,
        Field(
            description="Path to the metadata tree root directory. By default git repository root.",
        ),
    ] = ".",
    arch: Annotated[
        str,
        Field(
            description="Architecture to test against, by default 'x86_64'.",
        ),
    ] = Architecture.x86_64,
    plan_name: Annotated[
        str | None,
        Field(
            description="Selected plans to be executed. Can be a regular expression.",
        ),
    ] = None,
    test_name: Annotated[
        str | None,
        Field(
            description="Select tests to be executed. Can be a regular expression.",
        ),
    ] = None,
    context: Annotated[
        dict[str, str] | None,
        Field(
            description="TMT context variables as key-value pairs (e.g., {'distro': 'centos-stream', 'arch': 'x86_64'}).",  # noqa: E501
        ),
    ] = None,
    environment: Annotated[
        dict[str, str] | None,
        Field(
            description="TMT environment variables as key-value pairs (e.g., {'ROOTLESS_USER': 'ec2-user'}).",
        ),
    ] = None,
) -> dict[str, Any]:
    """Submit a test request to Testing Farm.

    The test repository must contain tmt metadata which define
    the test plans to be executed.

    Args:
        url: Git repository URL containing the tmt metadata
        compose: Compose to run tests against
        ref: Git branch, tag or commit specifying the desired git revision
        metadata_root_dir: Path to the metadata tree root directory
        plan_name: Selected plans to be executed (can be a regular expression)
        test_name: Select tests to be executed (can be a regular expression)
        arch: Architecture to test against
        context: TMT context variables as key-value pairs
        environment: TMT environment variables as key-value pairs

    Returns:
        Testing Farm request creation response
    """
    client = TestingFarmClient()
    try:
        # Build environment configuration
        env_config = {
            "arch": arch,
            "os": {
                "compose": compose,
            },
        }

        # Add TMT configuration if context or environment variables are provided
        if context or environment:
            tmt_config = {}
            if context:
                tmt_config["context"] = context
            if environment:
                tmt_config["environment"] = environment
            env_config["tmt"] = tmt_config

        environments = [env_config]

        test = {
            "tmt": {
                "url": url,
                "ref": ref,
                "path": metadata_root_dir,
                "test_name": test_name,
                "name": plan_name,
            },
        }

        return await client.submit_request(
            request={
                "test": test,
                "environments": environments,
            },
        )

    finally:
        await client.close()


@mcp.tool()  # type: ignore[misc]
async def list_composes(
    ranch: str = Field(
        Ranch.public,
        description="Ranch to list composes for, redhat or public.",
    ),
) -> list[str]:
    """List available composes for a ranch.

    Retrieve the list of supported composes available for testing
    in the specified ranch. Composes are the base operating system images
    that tests will run on.

    Args:
        ranch: Ranch name, 'redhat' or 'public'. By default 'public'.

    Returns:
        List of available composes with their names
    """
    client = TestingFarmClient()

    try:
        composes = await client.list_composes(ranch=ranch)
        return [
            compose
            for compose in composes
            # Hide compose regexes in the listing and also the deprecated stuff
            if "\\" not in compose and "+" not in compose and "*" not in compose and "aarch64" not in compose
        ]

    finally:
        await client.close()


@mcp.tool()  # type: ignore[misc]
async def get_request(
    request_id: str = Field(
        ...,
        description="Testing Farm request ID or a string containing the ID, like an API request URL or artifacts URL.",
    ),
) -> str:
    """Get details about a Testing Farm request.

    Extracts request ID from the provided string and retrieves request details.

    Args:
        request_id: Testing Farm request ID or a string containing the ID, like an API request URL or artifacts URL.

    Returns:
        Testing Farm request details or error message if request ID not found
    """
    client = TestingFarmClient()

    # UUID pattern
    uuid_pattern = re.compile("[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}")

    # Find the UUID in the string
    request_id_match = uuid_pattern.search(request_id)
    if not request_id_match:
        return f"Error: could not find request ID in {request_id}"

    request_id = request_id_match.group()

    try:
        return await client.get_request(request_id)

    finally:
        await client.close()


def main() -> None:
    """Run the MCP server."""
    mcp.run()
