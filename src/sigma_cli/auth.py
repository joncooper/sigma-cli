"""OAuth2 authentication for Sigma Computing API."""

import time
from typing import Optional
from urllib.parse import urljoin

import httpx
from rich.console import Console

from sigma_cli.config import SigmaConfig

console = Console()


class TokenCache:
    """Simple in-memory token cache."""

    def __init__(self):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expires_at: float = 0

    def is_expired(self) -> bool:
        """Check if the current token is expired (with 60s buffer)."""
        return time.time() >= (self.expires_at - 60)

    def set_tokens(
        self, access_token: str, refresh_token: str, expires_in: int
    ) -> None:
        """Store tokens with expiration time."""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = time.time() + expires_in


class SigmaAuth:
    """OAuth2 authentication handler for Sigma Computing API."""

    def __init__(self, config: SigmaConfig):
        self.config = config
        self.cache = TokenCache()

    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token

        Raises:
            httpx.HTTPStatusError: If authentication fails
        """
        # Return cached token if still valid
        if self.cache.access_token and not self.cache.is_expired():
            return self.cache.access_token

        # Try to refresh token if we have one
        if self.cache.refresh_token and self.cache.is_expired():
            try:
                return self._refresh_token()
            except Exception:
                # If refresh fails, get new token
                pass

        # Get new token
        return self._get_new_token()

    def _get_new_token(self) -> str:
        """
        Request a new access token using client credentials.

        Returns:
            New access token

        Raises:
            httpx.HTTPStatusError: If authentication fails
        """
        token_url = urljoin(self.config.base_url, "/v2/auth/token")

        # IMPORTANT: Use form-urlencoded, NOT Basic Auth header
        data = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.secret,
        }

        with httpx.Client() as client:
            response = client.post(
                token_url,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )

            # Better error handling - show API response
            if response.status_code != 200:
                try:
                    error_detail = response.json()
                    console.print(
                        f"[red]Authentication failed:[/red] {error_detail}",
                        style="bold"
                    )
                except Exception:
                    console.print(
                        f"[red]Authentication failed:[/red] {response.text}",
                        style="bold"
                    )

            response.raise_for_status()
            token_data = response.json()

            # Cache the tokens
            self.cache.set_tokens(
                access_token=token_data["access_token"],
                refresh_token=token_data["refresh_token"],
                expires_in=token_data["expires_in"],
            )

            return token_data["access_token"]

    def _refresh_token(self) -> str:
        """
        Refresh the access token using the refresh token.

        Returns:
            New access token

        Raises:
            httpx.HTTPStatusError: If refresh fails
        """
        token_url = urljoin(self.config.base_url, "/v2/auth/token")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.cache.refresh_token,
            "client_id": self.config.client_id,
            "client_secret": self.config.secret,
        }

        with httpx.Client() as client:
            response = client.post(
                token_url,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )

            response.raise_for_status()
            token_data = response.json()

            # Update cache
            self.cache.set_tokens(
                access_token=token_data["access_token"],
                refresh_token=token_data["refresh_token"],
                expires_in=token_data["expires_in"],
            )

            return token_data["access_token"]

    def get_auth_headers(self) -> dict[str, str]:
        """
        Get authentication headers for API requests.

        Returns:
            Dictionary with Authorization header
        """
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}
