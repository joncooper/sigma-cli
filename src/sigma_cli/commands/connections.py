"""Connection management commands."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from sigma_cli.client import SigmaClient
from sigma_cli.config import get_config
from sigma_cli.utils.json_utils import read_json_input
from sigma_cli.utils.output import print_error, print_json, print_success, print_table

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
def list_connections(
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Number of results"),
    page: Optional[str] = typer.Option(None, "--page", "-p", help="Page token"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search query"),
    include_archived: bool = typer.Option(False, "--archived", help="Include archived"),
    table: bool = typer.Option(False, "--table", "-t", help="Display as table"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """List all connections."""
    try:
        client = get_client(client_id, secret, base_url)

        params = {}
        if limit:
            params["limit"] = limit
        if page:
            params["page"] = page
        if search:
            params["search"] = search
        if include_archived:
            params["includeArchived"] = True

        response = client.get("/v2/connections", params=params)

        if table and "entries" in response:
            entries = response["entries"]
            columns = ["connectionId", "name", "type", "isSample"]
            print_table(entries, columns=columns, title="Connections")
        else:
            print_json(response, pretty=pretty, highlight=True)

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("get")
def get_connection(
    connection_id: str = typer.Argument(..., help="Connection ID"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Get a specific connection by ID."""
    try:
        client = get_client(client_id, secret, base_url)
        response = client.get(f"/v2/connections/{connection_id}")
        print_json(response, pretty=pretty, highlight=True)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("test")
def test_connection(
    connection_id: str = typer.Argument(..., help="Connection ID"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Test a connection."""
    try:
        client = get_client(client_id, secret, base_url)
        response = client.post(f"/v2/connections/{connection_id}/test")
        print_json(response, pretty=pretty, highlight=True)
        print_success("Connection test completed!")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)
