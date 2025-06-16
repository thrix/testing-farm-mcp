"""Testing Farm API client."""

import os
from typing import Any, cast

import httpx


class TestingFarmClient:
    """Client for Testing Farm API."""

    DEFAULT_API_URL = "https://api.testing-farm.io/v0.1"

    def __init__(self) -> None:
        """Initialize the Testing Farm client."""
        self.api_token = os.getenv("TESTING_FARM_API_TOKEN")
        if not self.api_token:
            msg = "TESTING_FARM_API_TOKEN must be provided"
            raise ValueError(msg)

        self.api_url = os.getenv("TESTING_FARM_API_URL") or self.DEFAULT_API_URL

        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={"Authorization": f"Bearer {self.api_token}"},
            timeout=30.0,
        )

    async def submit_request(
        self,
        request: dict[str, Any],
    ) -> dict[str, Any]:
        """Submit a test request to Testing Farm.

        Args:
            request: Testing Farm request

        Returns:
            Response from Testing Farm

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.post(
            "/requests",
            json=request,
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            return cast("dict[str, Any]", error.response.json())

        return cast("dict[str, Any]", response.json())

    async def list_composes(self, ranch: str) -> list[str]:
        """List available composes for a ranch.

        Args:
            ranch: Ranch to list composes for (redhat or public)

        Returns:
            List of available compose names

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.get(f"/composes/{ranch}")

        response.raise_for_status()

        return [str(compose["name"]) for compose in response.json()["composes"]]

    async def get_request(self, request_id: str) -> str:
        """Get Testing Farm request details.

        Args:
            request_id: Testing Farm request ID

        Returns:
            Human-readable status information about the Testing Farm request.

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        response = await self.client.get(f"/requests/{request_id}")
        response.raise_for_status()

        request = response.json()
        state = request["state"]

        if state == "new":
            return "The request was created and Testing Farm is preparing to run it."

        if state == "queued":
            return "The request is queued and Testing Farm is preparing to run it."

        artifacts = (request.get("run", {}) or {}).get("artifacts")
        summary = (request.get("result", {}) or {}).get("summary")
        overall = (request.get("result", {}) or {}).get("overall")

        if state in ["running", "error", "canceled", "cancel-requested"]:
            message = f"The request is {state}."
            message += f" {summary}." if summary else ""
            message += f" See {artifacts} for details." if artifacts else ""
            return message

        if state == "complete":
            message = f"The request is {state}."
            message += f" Tests have {overall}." if overall else ""
            message += f" {summary}." if summary else ""
            message += f" See {artifacts} for details." if artifacts else ""
            return message

        return f"The request is in unknown state: {state}"

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
