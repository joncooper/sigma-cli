"""Output formatting utilities using Rich."""

import json
from typing import Any

from rich.console import Console
from rich.json import JSON
from rich.table import Table
from rich.tree import Tree

console = Console()


def print_json(
    data: Any, pretty: bool = True, highlight: bool = True
) -> None:
    """
    Print JSON data with optional formatting and syntax highlighting.

    Args:
        data: Data to print (will be JSON-serialized)
        pretty: Whether to pretty-print (indent)
        highlight: Whether to use syntax highlighting
    """
    if highlight:
        # Use Rich's JSON formatter with syntax highlighting
        json_str = json.dumps(data, indent=2 if pretty else None)
        console.print(JSON(json_str))
    else:
        # Plain JSON output
        json_str = json.dumps(
            data, indent=2 if pretty else None, ensure_ascii=False
        )
        console.print(json_str)


def print_table(
    data: list[dict],
    columns: list[str] = None,
    title: str = None,
    max_width: int = None,
) -> None:
    """
    Print data as a formatted table.

    Args:
        data: List of dictionaries to display
        columns: Column names to display (default: all keys from first item)
        title: Table title
        max_width: Maximum column width
    """
    if not data:
        console.print("[yellow]No data to display[/yellow]")
        return

    # Determine columns
    if columns is None:
        columns = list(data[0].keys()) if data else []

    # Create table
    table = Table(title=title, show_header=True, header_style="bold magenta")

    # Add columns
    for col in columns:
        table.add_column(col, max_width=max_width, overflow="fold")

    # Add rows
    for item in data:
        row = [str(item.get(col, "")) for col in columns]
        table.add_row(*row)

    console.print(table)


def print_tree(data: dict, label: str = "Root") -> None:
    """
    Print nested dictionary as a tree structure.

    Args:
        data: Dictionary to display
        label: Root node label
    """

    def add_tree_items(tree: Tree, data: Any) -> None:
        """Recursively add items to tree."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    branch = tree.add(f"[bold]{key}[/bold]")
                    add_tree_items(branch, value)
                else:
                    tree.add(f"[bold]{key}:[/bold] {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    branch = tree.add(f"[bold][{i}][/bold]")
                    add_tree_items(branch, item)
                else:
                    tree.add(f"[bold][{i}]:[/bold] {item}")

    root = Tree(f"[bold cyan]{label}[/bold cyan]")
    add_tree_items(root, data)
    console.print(root)


def print_error(message: str, details: str = None) -> None:
    """
    Print an error message.

    Args:
        message: Error message
        details: Optional error details
    """
    console.print(f"[red bold]Error:[/red bold] {message}")
    if details:
        console.print(f"[red]{details}[/red]")


def print_success(message: str) -> None:
    """
    Print a success message.

    Args:
        message: Success message
    """
    console.print(f"[green bold]✓[/green bold] {message}")


def print_warning(message: str) -> None:
    """
    Print a warning message.

    Args:
        message: Warning message
    """
    console.print(f"[yellow bold]⚠[/yellow bold] {message}")


def print_info(message: str) -> None:
    """
    Print an info message.

    Args:
        message: Info message
    """
    console.print(f"[cyan bold]ℹ[/cyan bold] {message}")
