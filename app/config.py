"""Configuration loader for TETSUO display."""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Application configuration."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Load configuration from YAML file and environment.

        Args:
            config_path: Path to config.yaml
        """
        # Load environment variables
        load_dotenv()

        # Load YAML config
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file, 'r') as f:
            self.data = yaml.safe_load(f)

        # Add environment variables
        self.birdeye_api_key = os.getenv("BIRDEYE_API_KEY", "")

        # Ensure data directory exists
        cache_path = Path(self.data["cache"]["path"])
        cache_path.parent.mkdir(parents=True, exist_ok=True)

    def get(self, key_path: str, default=None):
        """
        Get a config value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., "token.symbol")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.data

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value):
        """
        Set a config value using dot notation.

        Args:
            key_path: Dot-separated path (e.g., "primary.pair")
            value: Value to set
        """
        keys = key_path.split('.')
        target = self.data

        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        target[keys[-1]] = value

    def save(self, config_path: str = "config.yaml"):
        """
        Save configuration back to YAML file.

        Args:
            config_path: Path to config.yaml
        """
        with open(config_path, 'w') as f:
            yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)

    @property
    def token_mint(self) -> str:
        """Get token mint address."""
        return self.get("token.mint")

    @property
    def token_symbol(self) -> str:
        """Get token symbol."""
        return self.get("token.symbol")

    @property
    def token_chain(self) -> str:
        """Get token chain."""
        return self.get("token.chain")

    @property
    def primary_pair(self) -> str:
        """Get primary trading pair address."""
        return self.get("primary.pair", "")

    @property
    def poll_interval(self) -> int:
        """Get polling interval in seconds."""
        return self.get("poll.interval_seconds", 45)

    @property
    def request_timeout(self) -> int:
        """Get request timeout in seconds."""
        return self.get("timeouts.seconds", 5)

    @property
    def max_retries(self) -> int:
        """Get max retry count."""
        return self.get("retries.max", 1)

    @property
    def cache_path(self) -> str:
        """Get cache file path."""
        return self.get("cache.path", "./data/last_snapshot.json")
