"""Tag management commands."""

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
def list_tags(
    inode_id: Optional[str] = typer.Option(None, "--inode-id", help="Filter by inode ID"),
    table: bool = typer.Option(False, "--table", "-t", help="Display as table"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Get tags."""
    try:
        client = get_client(client_id, secret, base_url)

        params = {}
        if inode_id:
            params["inodeId"] = inode_id

        response = client.get("/v2/tags", params=params)

        if table and isinstance(response, list):
            columns = ["tagId", "name", "color"]
            print_table(response, columns=columns, title="Tags")
        else:
            print_json(response, pretty=pretty, highlight=True)

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("create")
def create_tag(
    name: Optional[str] = typer.Option(None, "--name", help="Tag name"),
    color: Optional[str] = typer.Option(None, "--color", help="Tag color"),
    json_str: Optional[str] = typer.Option(None, "--json", "-j", help="JSON data"),
    json_file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Create a tag."""
    try:
        client = get_client(client_id, secret, base_url)

        json_data = read_json_input(json_str=json_str, json_file=json_file, use_stdin=True)
        if not json_data:
            json_data = {}
        if name:
            json_data["name"] = name
        if color:
            json_data["color"] = color

        if not json_data:
            print_error("No data provided. Use --name, --color, --json, --file, or pipe JSON to stdin")
            raise typer.Exit(1)

        response = client.post("/v2/tags", json_data=json_data)
        print_json(response, pretty=pretty, highlight=True)
        print_success("Tag created successfully!")

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("update")
def update_tag(
    tag_id: str = typer.Argument(..., help="Tag ID"),
    name: Optional[str] = typer.Option(None, "--name", help="Tag name"),
    color: Optional[str] = typer.Option(None, "--color", help="Tag color"),
    json_str: Optional[str] = typer.Option(None, "--json", "-j", help="JSON data"),
    json_file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Update a tag."""
    try:
        client = get_client(client_id, secret, base_url)

        json_data = read_json_input(json_str=json_str, json_file=json_file, use_stdin=True)
        if not json_data:
            json_data = {}
        if name:
            json_data["name"] = name
        if color:
            json_data["color"] = color

        if not json_data:
            print_error("No data provided")
            raise typer.Exit(1)

        response = client.patch(f"/v2/tags/{tag_id}", json_data=json_data)
        print_json(response, pretty=pretty, highlight=True)
        print_success("Tag updated successfully!")

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("delete")
def delete_tag(
    tag_id: str = typer.Argument(..., help="Tag ID"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Delete a tag."""
    try:
        client = get_client(client_id, secret, base_url)
        client.delete(f"/v2/tags/{tag_id}")
        print_success(f"Tag {tag_id} deleted successfully!")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("assign")
def assign_tag(
    tag_id: str = typer.Argument(..., help="Tag ID"),
    inode_id: str = typer.Argument(..., help="Inode ID to tag"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Assign a tag to a document."""
    try:
        client = get_client(client_id, secret, base_url)
        client.put(f"/v2/tags/{tag_id}/files/{inode_id}")
        print_success(f"Tag {tag_id} assigned to {inode_id}!")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)
