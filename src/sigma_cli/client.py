"""HTTP client for Sigma Computing REST API."""

from typing import Any, Optional
from urllib.parse import urljoin

import httpx
from rich.console import Console

from sigma_cli.auth import SigmaAuth
from sigma_cli.config import SigmaConfig

console = Console()


class SigmaClient:
    """HTTP client for interacting with the Sigma Computing REST API."""

    def __init__(self, config: SigmaConfig, verbose: bool = False):
        self.config = config
        self.auth = SigmaAuth(config)
        self.base_url = config.base_url
        self.verbose = verbose

    def _get_headers(self, extra_headers: Optional[dict] = None) -> dict[str, str]:
        """Build request headers with authentication."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        headers.update(self.auth.get_auth_headers())
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        # Ensure path starts with /
        if not path.startswith("/"):
            path = f"/{path}"
        return urljoin(self.base_url, path)

    def request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> Any:
        """
        Make an HTTP request to the Sigma API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path: API endpoint path (e.g., '/v2/workbooks')
            params: Query parameters
            json_data: JSON request body
            data: Form data (alternative to json_data)
            headers: Additional headers

        Returns:
            Response JSON data

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        url = self._build_url(path)
        request_headers = self._get_headers(headers)

        # Special handling for form data (e.g., token endpoint)
        if data is not None:
            request_headers["Content-Type"] = "application/x-www-form-urlencoded"

        # Verbose output for debugging
        if self.verbose:
            console.print(f"\n[bold cyan]HTTP Request:[/bold cyan]")
            console.print(f"  [dim]Method:[/dim] {method.upper()}")
            console.print(f"  [dim]URL:[/dim] {url}")
            if params:
                console.print(f"  [dim]Query params:[/dim] {params}")
            if json_data:
                import json
                console.print(f"  [dim]Request body:[/dim]")
                console.print(f"    {json.dumps(json_data, indent=2)}")
            console.print()

        with httpx.Client() as client:
            response = client.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json_data,
                data=data,
                headers=request_headers,
            )

            # Handle errors
            if not response.is_success:
                self._handle_error(response)

            # Return empty dict for 204 No Content
            if response.status_code == 204:
                return {}

            # Parse and return JSON response
            try:
                return response.json()
            except Exception:
                return response.text

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle API errors with helpful messages."""
        try:
            error_data = response.json()
            message = error_data.get("message", "Unknown error")
            code = error_data.get("code", "UNKNOWN")
            request_id = error_data.get("requestId", "N/A")

            console.print(
                f"[red bold]API Error ({response.status_code})[/red bold]",
                style="bold",
            )
            console.print(f"[red]Message:[/red] {message}")
            console.print(f"[red]Code:[/red] {code}")
            console.print(f"[red]Request ID:[/red] {request_id}")
        except Exception:
            console.print(
                f"[red bold]HTTP Error {response.status_code}[/red bold]",
                style="bold",
            )
            console.print(f"[red]{response.text}[/red]")

        response.raise_for_status()

    # Convenience methods for common HTTP verbs
    def get(self, path: str, params: Optional[dict] = None, **kwargs) -> Any:
        """Make a GET request."""
        return self.request("GET", path, params=params, **kwargs)

    def post(
        self,
        path: str,
        json_data: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ) -> Any:
        """Make a POST request."""
        return self.request("POST", path, json_data=json_data, data=data, **kwargs)

    def put(self, path: str, json_data: Optional[dict] = None, **kwargs) -> Any:
        """Make a PUT request."""
        return self.request("PUT", path, json_data=json_data, **kwargs)

    def patch(self, path: str, json_data: Optional[dict] = None, **kwargs) -> Any:
        """Make a PATCH request."""
        return self.request("PATCH", path, json_data=json_data, **kwargs)

    def delete(self, path: str, **kwargs) -> Any:
        """Make a DELETE request."""
        return self.request("DELETE", path, **kwargs)
