"""Dataset management commands."""

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
def list_datasets(
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Number of results"),
    page: Optional[str] = typer.Option(None, "--page", "-p", help="Page token"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search query"),
    table: bool = typer.Option(False, "--table", "-t", help="Display as table"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """List all datasets."""
    try:
        client = get_client(client_id, secret, base_url)

        params = {}
        if limit:
            params["limit"] = limit
        if page:
            params["page"] = page
        if search:
            params["search"] = search

        response = client.get("/v2/datasets", params=params)

        if table and "entries" in response:
            entries = response["entries"]
            columns = ["datasetId", "name", "type", "createdBy"]
            print_table(entries, columns=columns, title="Datasets")
        else:
            print_json(response, pretty=pretty, highlight=True)

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("get")
def get_dataset(
    dataset_id: str = typer.Argument(..., help="Dataset ID"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Get a specific dataset by ID."""
    try:
        client = get_client(client_id, secret, base_url)
        response = client.get(f"/v2/datasets/{dataset_id}")
        print_json(response, pretty=pretty, highlight=True)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("grants")
def get_grants(
    dataset_id: str = typer.Argument(..., help="Dataset ID"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Get grants for a dataset."""
    try:
        client = get_client(client_id, secret, base_url)
        response = client.get(f"/v2/datasets/{dataset_id}/grants")
        print_json(response, pretty=pretty, highlight=True)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("create-grant")
def create_grant(
    dataset_id: str = typer.Argument(..., help="Dataset ID"),
    json_str: Optional[str] = typer.Option(None, "--json", "-j", help="JSON data"),
    json_file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Create a grant for a dataset."""
    try:
        client = get_client(client_id, secret, base_url)
        json_data = read_json_input(json_str=json_str, json_file=json_file, use_stdin=True)

        if not json_data:
            print_error("No data provided. Use --json, --file, or pipe JSON to stdin")
            raise typer.Exit(1)

        response = client.post(f"/v2/datasets/{dataset_id}/grants", json_data=json_data)
        print_json(response, pretty=pretty, highlight=True)
        print_success("Grant created successfully!")

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("update-grant")
def update_grant(
    dataset_id: str = typer.Argument(..., help="Dataset ID"),
    grant_id: str = typer.Argument(..., help="Grant ID"),
    json_str: Optional[str] = typer.Option(None, "--json", "-j", help="JSON data"),
    json_file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Update a grant for a dataset."""
    try:
        client = get_client(client_id, secret, base_url)
        json_data = read_json_input(json_str=json_str, json_file=json_file, use_stdin=True)

        if not json_data:
            print_error("No data provided")
            raise typer.Exit(1)

        response = client.patch(f"/v2/datasets/{dataset_id}/grants/{grant_id}", json_data=json_data)
        print_json(response, pretty=pretty, highlight=True)
        print_success("Grant updated successfully!")

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("delete-grant")
def delete_grant(
    dataset_id: str = typer.Argument(..., help="Dataset ID"),
    grant_id: str = typer.Argument(..., help="Grant ID"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Delete a grant for a dataset."""
    try:
        client = get_client(client_id, secret, base_url)
        client.delete(f"/v2/datasets/{dataset_id}/grants/{grant_id}")
        print_success(f"Grant {grant_id} deleted successfully!")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)
