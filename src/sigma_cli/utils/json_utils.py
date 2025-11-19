"""JSON input/output utilities."""

import json
import sys
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

console = Console()


def read_json_input(
    json_str: Optional[str] = None,
    json_file: Optional[Path] = None,
    use_stdin: bool = False,
) -> Optional[dict[str, Any]]:
    """
    Read JSON input from multiple sources.

    Priority:
    1. json_str (direct JSON string)
    2. json_file (path to JSON file)
    3. stdin (if use_stdin=True and stdin is not a tty)

    Args:
        json_str: JSON string
        json_file: Path to JSON file
        use_stdin: Whether to read from stdin if no other source

    Returns:
        Parsed JSON dictionary or None

    Raises:
        json.JSONDecodeError: If JSON is invalid
    """
    # Direct JSON string
    if json_str:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON string: {e}[/red]")
            raise

    # JSON file
    if json_file:
        try:
            with open(json_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            console.print(f"[red]File not found: {json_file}[/red]")
            raise
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON in file {json_file}: {e}[/red]")
            raise

    # Stdin (only if not a tty, i.e., piped input)
    if use_stdin and not sys.stdin.isatty():
        try:
            stdin_content = sys.stdin.read().strip()
            if stdin_content:
                return json.loads(stdin_content)
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON from stdin: {e}[/red]")
            raise

    return None


def merge_json_with_params(
    json_data: Optional[dict], **params
) -> dict[str, Any]:
    """
    Merge JSON data with CLI parameters.

    CLI parameters override JSON data.

    Args:
        json_data: Base JSON data
        **params: CLI parameters (None values are filtered out)

    Returns:
        Merged dictionary
    """
    result = json_data.copy() if json_data else {}

    # Filter out None values from params
    filtered_params = {k: v for k, v in params.items() if v is not None}

    result.update(filtered_params)
    return result
