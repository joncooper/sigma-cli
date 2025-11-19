"""Member management commands."""

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
    return SigmaClient(cfg, verbose=verbose)


@app.command("list")
def list_members(
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Number of results"),
    page: Optional[str] = typer.Option(None, "--page", "-p", help="Page token"),
    table: bool = typer.Option(False, "--table", "-t", help="Display as table"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """List all members."""
    try:
        client = get_client(client_id, secret, base_url)

        params = {}
        if limit:
            params["limit"] = limit
        if page:
            params["page"] = page

        response = client.get("/v2/members", params=params)

        if table and "entries" in response:
            entries = response["entries"]
            columns = ["memberId", "email", "firstName", "lastName", "accountType"]
            print_table(entries, columns=columns, title="Members")
        else:
            print_json(response, pretty=pretty, highlight=True)

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("get")
def get_member(
    member_id: str = typer.Argument(..., help="Member ID"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Get a specific member by ID."""
    try:
        client = get_client(client_id, secret, base_url)
        response = client.get(f"/v2/members/{member_id}")
        print_json(response, pretty=pretty, highlight=True)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("create")
def create_member(
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Member email (required)"),
    first_name: Optional[str] = typer.Option(None, "--first-name", help="First name (required)"),
    last_name: Optional[str] = typer.Option(None, "--last-name", help="Last name (required)"),
    member_type: Optional[str] = typer.Option(None, "--member-type", "-m", help="Account type e.g. 'Viewer', 'Creator' (required)"),
    teams: Optional[str] = typer.Option(None, "--teams", "-t", help="Comma-separated team IDs to add member to"),
    user_kind: Optional[str] = typer.Option(None, "--user-kind", "-k", help="User kind: internal, guest, or embed"),
    send_invite: bool = typer.Option(True, "--send-invite/--no-invite", help="Send email invitation (default: true)"),
    json_str: Optional[str] = typer.Option(None, "--json", "-j", help="JSON data (overrides other options)"),
    json_file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file (overrides other options)"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show HTTP request details"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Create a new member in the organization.

    Required fields: email, first-name, last-name, member-type

    Example:
        sigma members create --email alice@example.com --first-name Alice --last-name Smith --member-type Viewer
    """
    try:
        client = get_client(client_id, secret, base_url, verbose=verbose)

        # Check for JSON input first
        json_data = read_json_input(json_str=json_str, json_file=json_file, use_stdin=True)
        if not json_data:
            json_data = {}

        # Apply CLI options if not provided in JSON
        if email and "email" not in json_data:
            json_data["email"] = email
        if first_name and "firstName" not in json_data:
            json_data["firstName"] = first_name
        if last_name and "lastName" not in json_data:
            json_data["lastName"] = last_name
        if member_type and "memberType" not in json_data:
            json_data["memberType"] = member_type
        if user_kind and "userKind" not in json_data:
            json_data["userKind"] = user_kind
        if teams and "addToTeams" not in json_data:
            team_list = [{"teamId": t.strip()} for t in teams.split(",")]
            json_data["addToTeams"] = team_list

        # Validate required fields
        missing = []
        for field, display in [("email", "email"), ("firstName", "first-name"),
                               ("lastName", "last-name"), ("memberType", "member-type")]:
            if field not in json_data:
                missing.append(f"--{display}")

        if missing:
            print_error(f"Missing required fields: {', '.join(missing)}")
            print_error("Use --json or --file to provide all fields, or specify each required option")
            raise typer.Exit(1)

        # sendInvite is a query parameter, not body
        params = {"sendInvite": str(send_invite).lower()}

        response = client.post("/v2/members", json_data=json_data, params=params)
        print_json(response, pretty=pretty, highlight=True)
        print_success("Member created successfully!")

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("update")
def update_member(
    member_id: str = typer.Argument(..., help="Member ID"),
    json_str: Optional[str] = typer.Option(None, "--json", "-j", help="JSON data"),
    json_file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Update a member."""
    try:
        client = get_client(client_id, secret, base_url)

        json_data = read_json_input(json_str=json_str, json_file=json_file, use_stdin=True)
        if not json_data:
            print_error("No data provided")
            raise typer.Exit(1)

        response = client.patch(f"/v2/members/{member_id}", json_data=json_data)
        print_json(response, pretty=pretty, highlight=True)
        print_success("Member updated successfully!")

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("delete")
def delete_member(
    member_id: str = typer.Argument(..., help="Member ID"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Delete a member."""
    try:
        client = get_client(client_id, secret, base_url)
        client.delete(f"/v2/members/{member_id}")
        print_success(f"Member {member_id} deleted successfully!")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("teams")
def get_member_teams(
    member_id: str = typer.Argument(..., help="Member ID"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Get teams for a member."""
    try:
        client = get_client(client_id, secret, base_url)
        response = client.get(f"/v2/members/{member_id}/teams")
        print_json(response, pretty=pretty, highlight=True)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)
