"""Authentication commands."""

from typing import Optional

import typer
from rich.console import Console

from sigma_cli.client import SigmaClient
from sigma_cli.config import get_config
from sigma_cli.utils.output import print_error, print_json, print_success

app = typer.Typer()
console = Console()


@app.command("token")
def get_token(
    client_id: Optional[str] = typer.Option(
        None, "--client-id", envvar="SIGMA_CLIENT_ID"
    ),
    secret: Optional[str] = typer.Option(
        None, "--secret", envvar="SIGMA_SECRET"
    ),
    base_url: str = typer.Option(
        "https://aws-api.sigmacomputing.com/v2",
        "--base-url",
        envvar="SIGMA_BASE_URL",
    ),
    pretty: bool = typer.Option(
        True, "--pretty/--compact", help="Pretty-print JSON output"
    ),
):
    """
    Get an access token.

    Returns a fresh access token that can be used for API authentication.
    """
    try:
        cfg = get_config(client_id=client_id, secret=secret, base_url=base_url)

        if not cfg.validate_credentials():
            print_error("Missing credentials. Please configure sigma-cli first.")
            raise typer.Exit(1)

        client = SigmaClient(cfg)
        token = client.auth.get_access_token()

        result = {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        print_json(result, pretty=pretty, highlight=True)

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)
