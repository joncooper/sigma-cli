"""Workbook management commands."""

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


def get_client(client_id, secret, base_url, verbose=False) -> SigmaClient:
    """Helper to create and validate client."""
    cfg = get_config(verbose=verbose, client_id=client_id, secret=secret, base_url=base_url)
    if not cfg.validate_credentials():
        print_error("Missing credentials. Please configure sigma-cli first.")
        raise typer.Exit(1)
    return SigmaClient(cfg)


@app.command("list")
def list_workbooks(
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Number of results"),
    page: Optional[str] = typer.Option(None, "--page", "-p", help="Page token"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search query"),
    table: bool = typer.Option(False, "--table", "-t", help="Display as table"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show configuration sources"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """List all workbooks."""
    try:
        client = get_client(client_id, secret, base_url, verbose=verbose)

        params = {}
        if limit:
            params["limit"] = limit
        if page:
            params["page"] = page
        if search:
            params["search"] = search

        response = client.get("/v2/workbooks", params=params)

        if table and "entries" in response:
            # Display as table
            entries = response["entries"]
            columns = ["workbookId", "name", "createdBy", "updatedAt"]
            print_table(entries, columns=columns, title="Workbooks")
        else:
            # Display as JSON
            print_json(response, pretty=pretty, highlight=True)

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("get")
def get_workbook(
    workbook_id: str = typer.Argument(..., help="Workbook ID"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show configuration sources"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Get a specific workbook by ID."""
    try:
        client = get_client(client_id, secret, base_url, verbose=verbose)
        response = client.get(f"/v2/workbooks/{workbook_id}")
        print_json(response, pretty=pretty, highlight=True)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("create")
def create_workbook(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Workbook name"),
    json_str: Optional[str] = typer.Option(None, "--json", "-j", help="JSON data"),
    json_file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show configuration sources"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Create a new workbook."""
    try:
        client = get_client(client_id, secret, base_url, verbose=verbose)

        # Get JSON data from various sources
        json_data = read_json_input(json_str=json_str, json_file=json_file, use_stdin=True)

        # Merge with CLI options
        if not json_data:
            json_data = {}
        if name:
            json_data["name"] = name

        if not json_data:
            print_error("No data provided. Use --name, --json, --file, or pipe JSON to stdin")
            raise typer.Exit(1)

        response = client.post("/v2/workbooks", json_data=json_data)
        print_json(response, pretty=pretty, highlight=True)
        print_success(f"Workbook created successfully!")

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("update")
def update_workbook(
    workbook_id: str = typer.Argument(..., help="Workbook ID"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Workbook name"),
    json_str: Optional[str] = typer.Option(None, "--json", "-j", help="JSON data"),
    json_file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show configuration sources"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Update a workbook."""
    try:
        client = get_client(client_id, secret, base_url, verbose=verbose)

        json_data = read_json_input(json_str=json_str, json_file=json_file, use_stdin=True)
        if not json_data:
            json_data = {}
        if name:
            json_data["name"] = name

        if not json_data:
            print_error("No data provided")
            raise typer.Exit(1)

        response = client.patch(f"/v2/workbooks/{workbook_id}", json_data=json_data)
        print_json(response, pretty=pretty, highlight=True)
        print_success("Workbook updated successfully!")

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("delete")
def delete_workbook(
    workbook_id: str = typer.Argument(..., help="Workbook ID"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show configuration sources"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Delete a workbook."""
    try:
        client = get_client(client_id, secret, base_url, verbose=verbose)
        client.delete(f"/v2/workbooks/{workbook_id}")
        print_success(f"Workbook {workbook_id} deleted successfully!")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)
