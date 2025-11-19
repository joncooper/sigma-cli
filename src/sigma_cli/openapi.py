"""OpenAPI specification parser for generating CLI commands."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

console = Console()

# Path to the OpenAPI spec (relative to package root)
OPENAPI_SPEC_PATH = Path(__file__).parent.parent.parent / "ref" / "sigma-computing-public-rest-api.json"


class OpenAPIParser:
    """Parser for Sigma Computing OpenAPI specification."""

    def __init__(self, spec_path: Path = OPENAPI_SPEC_PATH):
        self.spec_path = spec_path
        self.spec: Dict[str, Any] = {}
        self._load_spec()

    def _load_spec(self) -> None:
        """Load the OpenAPI specification from file."""
        try:
            with open(self.spec_path, "r") as f:
                self.spec = json.load(f)
        except FileNotFoundError:
            console.print(
                f"[red]OpenAPI spec not found at {self.spec_path}[/red]"
            )
            raise
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON in OpenAPI spec: {e}[/red]")
            raise

    def get_tags(self) -> List[str]:
        """Get all tags (command groups) from the spec."""
        tags = set()
        for path_data in self.spec.get("paths", {}).values():
            for operation in path_data.values():
                if isinstance(operation, dict) and "tags" in operation:
                    tags.update(operation["tags"])
        return sorted(tags)

    def get_operations_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all operations for a specific tag."""
        operations = []
        for path, path_data in self.spec.get("paths", {}).items():
            for method, operation in path_data.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    if isinstance(operation, dict) and tag in operation.get("tags", []):
                        operations.append(
                            {
                                "path": path,
                                "method": method.upper(),
                                "operation_id": operation.get("operationId", ""),
                                "summary": operation.get("summary", ""),
                                "description": operation.get("description", ""),
                                "parameters": operation.get("parameters", []),
                                "request_body": operation.get("requestBody", None),
                            }
                        )
        return operations

    def get_operation_by_id(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific operation by its operationId."""
        for path, path_data in self.spec.get("paths", {}).items():
            for method, operation in path_data.items():
                if (
                    isinstance(operation, dict)
                    and operation.get("operationId") == operation_id
                ):
                    return {
                        "path": path,
                        "method": method.upper(),
                        "operation_id": operation_id,
                        "summary": operation.get("summary", ""),
                        "description": operation.get("description", ""),
                        "parameters": operation.get("parameters", []),
                        "request_body": operation.get("requestBody", None),
                    }
        return None

    def get_all_operations(self) -> List[Dict[str, Any]]:
        """Get all operations from the spec."""
        operations = []
        for path, path_data in self.spec.get("paths", {}).items():
            for method, operation in path_data.items():
                if method.lower() in ["get", "post", "put", "patch", "delete"]:
                    if isinstance(operation, dict):
                        operations.append(
                            {
                                "path": path,
                                "method": method.upper(),
                                "operation_id": operation.get("operationId", ""),
                                "summary": operation.get("summary", ""),
                                "description": operation.get("description", ""),
                                "parameters": operation.get("parameters", []),
                                "request_body": operation.get("requestBody", None),
                                "tags": operation.get("tags", []),
                            }
                        )
        return operations


def get_parser() -> OpenAPIParser:
    """Get a cached OpenAPI parser instance."""
    return OpenAPIParser()
