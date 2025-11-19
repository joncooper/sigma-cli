"""Team management commands."""

import re
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

# UUID pattern for detection
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)


def is_uuid(value: str) -> bool:
    """Check if a string looks like a UUID."""
    return bool(UUID_PATTERN.match(value))


def resolve_team_id(client: SigmaClient, team_identifier: str) -> str:
    """Resolve a team name to its UUID, or return as-is if already a UUID."""
    if is_uuid(team_identifier):
        return team_identifier

    # Search for team by name
    response = client.get("/v2/teams")
    entries = response.get("entries", [])

    # Try exact match first
    for team in entries:
        if team.get("name", "").lower() == team_identifier.lower():
            team_id = team.get("teamId")
            console.print(f"[dim]Resolved team '{team_identifier}' -> {team_id}[/dim]")
            return team_id

    # Try partial match
    matches = [t for t in entries if team_identifier.lower() in t.get("name", "").lower()]
    if len(matches) == 1:
        team_id = matches[0].get("teamId")
        console.print(f"[dim]Resolved team '{team_identifier}' -> {team_id}[/dim]")
        return team_id
    elif len(matches) > 1:
        names = [t.get("name") for t in matches]
        raise ValueError(f"Ambiguous team name '{team_identifier}'. Matches: {', '.join(names)}")

    raise ValueError(f"Team not found: '{team_identifier}'")


def resolve_member_id(client: SigmaClient, member_identifier: str) -> str:
    """Resolve a member email to UUID, or return as-is if already a UUID."""
    if is_uuid(member_identifier):
        return member_identifier

    # Assume it's an email if it contains @, otherwise try as email anyway
    response = client.get("/v2/members")
    entries = response.get("entries", [])

    # Try exact email match
    for member in entries:
        if member.get("email", "").lower() == member_identifier.lower():
            member_id = member.get("memberId")
            console.print(f"[dim]Resolved member '{member_identifier}' -> {member_id}[/dim]")
            return member_id

    # Try matching by name (firstName lastName)
    for member in entries:
        full_name = f"{member.get('firstName', '')} {member.get('lastName', '')}".strip().lower()
        if full_name == member_identifier.lower():
            member_id = member.get("memberId")
            console.print(f"[dim]Resolved member '{member_identifier}' -> {member_id}[/dim]")
            return member_id

    raise ValueError(f"Member not found: '{member_identifier}'. Use email address or full name.")


def get_client(client_id, secret, base_url, verbose=False) -> SigmaClient:
    """Helper to create and validate client."""
    cfg = get_config(verbose=verbose, client_id=client_id, secret=secret, base_url=base_url)
    if not cfg.validate_credentials():
        print_error("Missing credentials. Please configure sigma-cli first.")
        raise typer.Exit(1)
    return SigmaClient(cfg, verbose=verbose)


@app.command("list")
def list_teams(
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Number of results"),
    page: Optional[str] = typer.Option(None, "--page", "-p", help="Page token"),
    table: bool = typer.Option(False, "--table", "-t", help="Display as table"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """List all teams."""
    try:
        client = get_client(client_id, secret, base_url)

        params = {}
        if limit:
            params["limit"] = limit
        if page:
            params["page"] = page

        response = client.get("/v2/teams", params=params)

        if table and "entries" in response:
            entries = response["entries"]
            columns = ["teamId", "name", "description"]
            print_table(entries, columns=columns, title="Teams")
        else:
            print_json(response, pretty=pretty, highlight=True)

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("get")
def get_team(
    team: str = typer.Argument(..., help="Team name or UUID"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Get a specific team by name or ID."""
    try:
        client = get_client(client_id, secret, base_url)
        team_id = resolve_team_id(client, team)
        response = client.get(f"/v2/teams/{team_id}")
        print_json(response, pretty=pretty, highlight=True)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("create")
def create_team(
    name: Optional[str] = typer.Option(None, "--name", help="Team name"),
    json_str: Optional[str] = typer.Option(None, "--json", "-j", help="JSON data"),
    json_file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Create a new team."""
    try:
        client = get_client(client_id, secret, base_url)

        json_data = read_json_input(json_str=json_str, json_file=json_file, use_stdin=True)
        if not json_data:
            json_data = {}
        if name:
            json_data["name"] = name

        if not json_data:
            print_error("No data provided. Use --name, --json, --file, or pipe JSON to stdin")
            raise typer.Exit(1)

        response = client.post("/v2/teams", json_data=json_data)
        print_json(response, pretty=pretty, highlight=True)
        print_success("Team created successfully!")

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("update")
def update_team(
    team: str = typer.Argument(..., help="Team name or UUID"),
    name: Optional[str] = typer.Option(None, "--name", help="New team name"),
    json_str: Optional[str] = typer.Option(None, "--json", "-j", help="JSON data"),
    json_file: Optional[Path] = typer.Option(None, "--file", "-f", help="JSON file"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Update a team."""
    try:
        client = get_client(client_id, secret, base_url)
        team_id = resolve_team_id(client, team)

        json_data = read_json_input(json_str=json_str, json_file=json_file, use_stdin=True)
        if not json_data:
            json_data = {}
        if name:
            json_data["name"] = name

        if not json_data:
            print_error("No data provided")
            raise typer.Exit(1)

        response = client.patch(f"/v2/teams/{team_id}", json_data=json_data)
        print_json(response, pretty=pretty, highlight=True)
        print_success("Team updated successfully!")

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("delete")
def delete_team(
    team: str = typer.Argument(..., help="Team name or UUID"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Delete a team."""
    try:
        client = get_client(client_id, secret, base_url)
        team_id = resolve_team_id(client, team)
        client.delete(f"/v2/teams/{team_id}")
        print_success(f"Team '{team}' deleted successfully!")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("members")
def get_team_members(
    team: str = typer.Argument(..., help="Team name or UUID"),
    pretty: bool = typer.Option(True, "--pretty/--compact", help="Pretty-print JSON"),
    table: bool = typer.Option(False, "--table", "-t", help="Display as table"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Get members of a team."""
    try:
        client = get_client(client_id, secret, base_url)
        team_id = resolve_team_id(client, team)
        response = client.get(f"/v2/teams/{team_id}/members")

        if table and isinstance(response, list):
            columns = ["memberId", "email", "firstName", "lastName"]
            print_table(response, columns=columns, title=f"Team '{team}' Members")
        else:
            print_json(response, pretty=pretty, highlight=True)
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("add-member")
def add_team_member(
    team: str = typer.Argument(..., help="Team name or UUID"),
    member: str = typer.Argument(..., help="Member email, name, or UUID"),
    admin: bool = typer.Option(False, "--admin", "-a", help="Make member a team admin"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show HTTP request details"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Add an existing member to a team.

    Examples:
        sigma teams add-member "Sales Team" alice@example.com
        sigma teams add-member northbridge "Alice Smith"

    Note: The member must already exist in the organization.
    To create a new member, use 'sigma members create' instead.
    """
    try:
        client = get_client(client_id, secret, base_url, verbose=verbose)

        # Resolve names to UUIDs
        team_id = resolve_team_id(client, team)
        member_id = resolve_member_id(client, member)

        json_data = {"add": [member_id]}
        client.patch(f"/v2/teams/{team_id}/members", json_data=json_data)
        print_success(f"Member '{member}' added to team '{team}'!")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command("remove-member")
def remove_team_member(
    team: str = typer.Argument(..., help="Team name or UUID"),
    member: str = typer.Argument(..., help="Member email, name, or UUID"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show HTTP request details"),
    client_id: Optional[str] = typer.Option(None, "--client-id", envvar="SIGMA_CLIENT_ID"),
    secret: Optional[str] = typer.Option(None, "--secret", envvar="SIGMA_SECRET"),
    base_url: str = typer.Option("https://aws-api.sigmacomputing.com/v2", "--base-url", envvar="SIGMA_BASE_URL"),
):
    """Remove a member from a team.

    Examples:
        sigma teams remove-member "Sales Team" alice@example.com
        sigma teams remove-member northbridge "Alice Smith"
    """
    try:
        client = get_client(client_id, secret, base_url, verbose=verbose)

        # Resolve names to UUIDs
        team_id = resolve_team_id(client, team)
        member_id = resolve_member_id(client, member)

        json_data = {"remove": [member_id]}
        client.patch(f"/v2/teams/{team_id}/members", json_data=json_data)
        print_success(f"Member '{member}' removed from team '{team}'!")
    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)
