"""Main CLI application for sigma-cli."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from sigma_cli.client import SigmaClient
from sigma_cli.config import SigmaConfig, get_config
from sigma_cli.utils.json_utils import merge_json_with_params, read_json_input
from sigma_cli.utils.output import (
    print_error,
    print_info,
    print_json,
    print_success,
)

# Create main app
app = typer.Typer(
    name="sigma",
    help="Command-line interface for Sigma Computing REST API",
    add_completion=True,
    rich_markup_mode="rich",
)

console = Console()

# Global options that apply to all commands
client_id_option = typer.Option(
    None,
    "--client-id",
    envvar="SIGMA_CLIENT_ID",
    help="Sigma API Client ID",
)
secret_option = typer.Option(
    None,
    "--secret",
    envvar="SIGMA_SECRET",
    help="Sigma API Secret",
)
base_url_option = typer.Option(
    "https://aws-api.sigmacomputing.com/v2",
    "--base-url",
    envvar="SIGMA_BASE_URL",
    help="Sigma API base URL",
)


@app.command()
def config(
    client_id: Optional[str] = typer.Option(
        None, "--client-id", help="Sigma API Client ID"
    ),
    secret: Optional[str] = typer.Option(
        None, "--secret", help="Sigma API Secret"
    ),
    base_url: Optional[str] = typer.Option(
        None,
        "--base-url",
        help="Sigma API base URL (default: https://aws-api.sigmacomputing.com/v2)",
    ),
    show: bool = typer.Option(
        False, "--show", help="Show current configuration"
    ),
):
    """
    Configure sigma-cli settings.

    Save configuration to ~/.sigma/config.json for persistent use.
    """
    if show:
        # Show current configuration
        cfg = get_config()
        config_data = {
            "client_id": cfg.client_id or "(not set)",
            "secret": "***" if cfg.secret else "(not set)",
            "base_url": cfg.base_url,
        }
        print_info("Current configuration:")
        print_json(config_data, pretty=True, highlight=True)
        return

    # Update configuration
    updates = {}
    if client_id is not None:
        updates["client_id"] = client_id
    if secret is not None:
        updates["secret"] = secret
    if base_url is not None:
        updates["base_url"] = base_url

    if not updates:
        print_error(
            "No configuration provided. Use --client-id, --secret, or --base-url."
        )
        raise typer.Exit(1)

    # Load existing config and update
    cfg = get_config(**updates)
    cfg.save()

    print_success("Configuration saved successfully!")


@app.command()
def raw(
    method: str = typer.Argument(
        ..., help="HTTP method (GET, POST, PUT, PATCH, DELETE)"
    ),
    path: str = typer.Argument(..., help="API endpoint path (e.g., /v2/workbooks)"),
    json_str: Optional[str] = typer.Option(
        None, "--json", "-j", help="JSON request body as string"
    ),
    json_file: Optional[Path] = typer.Option(
        None, "--file", "-f", help="JSON request body from file"
    ),
    params: Optional[str] = typer.Option(
        None, "--params", "-p", help="Query parameters as JSON"
    ),
    pretty: bool = typer.Option(
        True, "--pretty/--compact", help="Pretty-print JSON output"
    ),
    client_id: Optional[str] = client_id_option,
    secret: Optional[str] = secret_option,
    base_url: str = base_url_option,
):
    """
    Make a raw HTTP request to the Sigma API.

    Examples:
        sigma raw GET /v2/workbooks
        sigma raw GET /v2/workbooks --params '{"limit": 10}'
        sigma raw POST /v2/workbooks --json '{"name": "My Workbook"}'
        echo '{"name": "My Workbook"}' | sigma raw POST /v2/workbooks
    """
    try:
        # Load configuration
        cfg = get_config(client_id=client_id, secret=secret, base_url=base_url)

        # Validate credentials
        if not cfg.validate_credentials():
            print_error(
                "Missing credentials. Set SIGMA_CLIENT_ID and SIGMA_SECRET, "
                "or use --client-id and --secret options, "
                "or run 'sigma config' to save them."
            )
            raise typer.Exit(1)

        # Create client
        client = SigmaClient(cfg)

        # Parse request body (from stdin, file, or string)
        json_data = read_json_input(
            json_str=json_str, json_file=json_file, use_stdin=True
        )

        # Parse query parameters
        query_params = None
        if params:
            import json

            query_params = json.loads(params)

        # Make request
        response = client.request(
            method=method.upper(),
            path=path,
            params=query_params,
            json_data=json_data,
        )

        # Print response
        print_json(response, pretty=pretty, highlight=True)

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


@app.command()
def version():
    """Show sigma-cli version."""
    from sigma_cli import __version__

    print_info(f"sigma-cli version {__version__}")


# Import and register command groups
def register_commands():
    """Register all API command groups dynamically."""
    from sigma_cli.commands import (
        account_types,
        auth_cmd,
        connections,
        datasets,
        files,
        grants,
        members,
        tags,
        teams,
        user_attributes,
        whoami,
        workbooks,
        workspaces,
    )

    # Authentication and configuration
    app.add_typer(
        auth_cmd.app,
        name="auth",
        help="Authentication commands",
    )

    # User and team management
    app.add_typer(
        members.app,
        name="members",
        help="Manage organization members",
    )
    app.add_typer(
        teams.app,
        name="teams",
        help="Manage teams",
    )
    app.add_typer(
        account_types.app,
        name="account-types",
        help="Manage account types",
    )

    # Workbooks and content
    app.add_typer(
        workbooks.app,
        name="workbooks",
        help="Manage workbooks",
    )
    app.add_typer(
        datasets.app,
        name="datasets",
        help="Manage datasets",
    )
    app.add_typer(
        files.app,
        name="files",
        help="Manage files",
    )
    app.add_typer(
        workspaces.app,
        name="workspaces",
        help="Manage workspaces",
    )

    # Data infrastructure
    app.add_typer(
        connections.app,
        name="connections",
        help="Manage data connections",
    )

    # Permissions and organization
    app.add_typer(
        grants.app,
        name="grants",
        help="Manage grants and permissions",
    )
    app.add_typer(
        user_attributes.app,
        name="user-attributes",
        help="Manage user attributes",
    )
    app.add_typer(
        tags.app,
        name="tags",
        help="Manage tags",
    )

    # Utilities
    app.add_typer(
        whoami.app,
        name="whoami",
        help="Get current user information",
    )


# Register commands on import
register_commands()


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
