"""Configuration management for sigma-cli."""

import json
import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console

console = Console()

# Configuration directory
CONFIG_DIR = Path.home() / ".sigma"
CONFIG_FILE = CONFIG_DIR / "config.json"


class SigmaConfig(BaseSettings):
    """Sigma CLI configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="SIGMA_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    client_id: Optional[str] = Field(default=None, description="Sigma API Client ID")
    secret: Optional[str] = Field(default=None, description="Sigma API Secret")
    base_url: str = Field(
        default="https://aws-api.sigmacomputing.com/v2",
        description="Sigma API base URL",
    )

    @classmethod
    def load(cls, verbose: bool = False, **overrides) -> "SigmaConfig":
        """
        Load configuration from multiple sources with precedence:
        1. Overrides (CLI arguments) - highest priority
        2. Environment variables
        3. ~/.sigma/config.json
        4. Defaults - lowest priority
        """
        # Start with file config
        file_config = {}
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    file_config = json.load(f)
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Could not load config file: {e}[/yellow]"
                )

        # Filter out None values from overrides so they don't mask config file values
        overrides = {k: v for k, v in overrides.items() if v is not None}

        # Read environment variables explicitly (pydantic auto-reads them but we want control)
        env_config = {}
        for key in ["client_id", "secret", "base_url"]:
            env_key = f"SIGMA_{key.upper()}"
            env_value = os.getenv(env_key)
            if env_value:
                env_config[key] = env_value

        # Merge with proper precedence: file_config < env vars < overrides
        merged = {**file_config, **env_config, **overrides}

        # Verbose output showing credential sources
        if verbose:
            console.print("[bold]Configuration sources:[/bold]")
            for key in ["client_id", "secret", "base_url"]:
                value = merged.get(key)
                if key in overrides:
                    source = "CLI argument"
                elif key in env_config:
                    source = f"environment variable (SIGMA_{key.upper()})"
                elif key in file_config:
                    source = f"config file ({CONFIG_FILE})"
                else:
                    source = "default"

                # Mask sensitive values
                if value:
                    if key == "secret":
                        display_value = f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}" if len(value) > 8 else "***"
                    elif key == "client_id":
                        display_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else value
                    else:
                        display_value = value
                else:
                    display_value = "[not set]"

                console.print(f"  {key}: {display_value} [dim]({source})[/dim]")

        # Use model_validate to bypass pydantic's automatic env loading
        return cls.model_validate(merged)

    def save(self) -> None:
        """Save current configuration to ~/.sigma/config.json."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        config_data = {
            "client_id": self.client_id,
            "secret": self.secret,
            "base_url": self.base_url,
        }

        # Remove None values
        config_data = {k: v for k, v in config_data.items() if v is not None}

        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=2)

        # Set restrictive permissions (owner read/write only)
        CONFIG_FILE.chmod(0o600)

        console.print(
            f"[green]Configuration saved to {CONFIG_FILE}[/green]", style="bold"
        )

    def validate_credentials(self) -> bool:
        """Check if required credentials are present."""
        return bool(self.client_id and self.secret)


def get_config(verbose: bool = False, **overrides) -> SigmaConfig:
    """Convenience function to load configuration."""
    return SigmaConfig.load(verbose=verbose, **overrides)
