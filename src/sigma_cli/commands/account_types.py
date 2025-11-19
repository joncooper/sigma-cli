"""Account type management commands."""

from typing import Optional

import typer
from rich.console import Console

from sigma_cli.client import SigmaClient
from sigma_cli.config import get_config
from sigma_cli.utils.output import print_error, print_json, print_table

app = typer.Typer()
console = Console()


def get_client(client_id, secret, base_url) -> SigmaClient:
    """Helper to create and validate client."""
    cfg = get_config(client_id=client_id, secret=secret, base_url=base_url)
    if not cfg.validate_credentials():
        print_error("Missing credentials. Please configure sigma-cli first.")
        raise typer.Exit(1)
    return SigmaClient(cfg)


@app.command("list")
def list_account_types(
    page_size: Optional[int] = typer.Option(None, "--page-size", help="Page size"),
    page_token: Optional[str] = typer.Option(None, "--page-token", help="Page token"),
    table: bool = typer.Option(False, "--table", "-t", help="Display as table"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """List all account types."""
    try:
        client = get_client(client_id, secret, base_url)

        params = {}
        if page_size:
            params["pageSize"] = page_size
        if page_token:
            params["pageToken"] = page_token

        response = client.get("/v2/accountTypes", params=params)

        if table and "entries" in response:
            entries = response["entries"]
            columns = ["accountTypeId", "accountTypeName", "isCustom"]
            print_table(entries, columns=columns, title="Account Types")
        else:
            print_json(response, pretty=pretty, highlight=True)

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("permissions")
def get_permissions(
    account_type_id: str = typer.Argument(..., help="Account type ID"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Get permissions for an account type."""
    try:
        client = get_client(client_id, secret, base_url)
        response = client.get(f"/v2/accountTypes/{account_type_id}/permissions")
        print_json(response, pretty=pretty, highlight=True)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)
